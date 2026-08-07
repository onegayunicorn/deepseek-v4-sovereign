/*
 * SOVEREIGN BCI Ring — firmware/main.c
 * ------------------------------------------------------------------
 * Reference firmware sketch for the 22 mm neural ring.
 * Target: nRF52840 (Zephyr/Arduino-compatible HAL), ESP32-S3 drop-in.
 *
 * Sensors:
 *   - ADS1299  : 4-ch EEG, 24-bit, 500 SPS, SPI        (P0.08 CS / P0.10 DRDY)
 *   - MAX30102 : PPG IR+RED, 100 SPS, I2C 0x57         (P0.12 INT)
 *   - BMI270   : accel+gyro, 200 SPS, I2C 0x68         (P0.11 INT)
 * Radio:
 *   - BLE 5.0 GATT notify, 6 characteristics (see protocol.md)
 * Power:
 *   - 80 mAh LiPo, Qi + USB-C charging, DC-DC on
 *
 * Privacy-first: only fixed-point feature blocks leave the device;
 * raw waveform export is opt-in via the command characteristic.
 *
 * Style: Arduino-sketch-compatible C; heavily commented.
 */

#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* ------------------------------------------------------------------ */
/* Pin / bus configuration                                             */
/* ------------------------------------------------------------------ */
#define PIN_SPI_CS_EEG   8      /* ADS1299 chip select                 */
#define PIN_DRDY_EEG     10     /* ADS1299 data-ready IRQ              */
#define PIN_INT_PPG      12     /* MAX30102 proximity/fifo IRQ         */
#define PIN_INT_IMU      11     /* BMI270 data-ready IRQ               */
#define PIN_CHG_STAT     13     /* charger status input                */
#define PIN_LED_CYAN     14     /* status LED (brand cyan #00E5FF)     */
#define PIN_LED_MINT     15     /* status LED (brand mint #00FFCC)     */

#define I2C_ADDR_PPG     0x57
#define I2C_ADDR_IMU     0x68

/* ------------------------------------------------------------------ */
/* Protocol constants (mirror protocol.md)                             */
/* ------------------------------------------------------------------ */
#define PKT_SYNC        0x53
#define PKT_SIZE        20
#define TYPE_EEG        0x01
#define TYPE_PPG        0x02
#define TYPE_IMU        0x03
#define FLAG_RAW        0x80
#define FLAG_BLOCK_END  0x40

#define EEG_SPS         500
#define EEG_BLOCK       25      /* 20 Hz notify rate                   */
#define PPG_SPS         100
#define PPG_BLOCK       5
#define IMU_SPS         200
#define IMU_BLOCK       8

/* ------------------------------------------------------------------ */
/* Simulated sensor register maps (stub register reads)                */
/* ------------------------------------------------------------------ */
typedef struct {
    uint16_t theta_q;   /* fixed-point band powers, 0..4095            */
    uint16_t alpha_q;
    uint16_t beta_q;
    uint16_t gamma_q;
    uint8_t  blink_count;
    uint8_t  quality;   /* 0..255 signal quality                       */
    uint16_t rms_uv;    /* block RMS in µV                            */
} eeg_block_t;

typedef struct {
    uint16_t hr_bpm;    /* 0.01 BPM fixed                              */
    uint16_t hrv_ms;    /* 0.01 ms fixed                               */
    uint16_t spo2;      /* 0.01 % fixed                                */
    uint32_t ir_baseline;
    uint8_t  confidence;
    uint8_t  quality;
} ppg_block_t;

typedef struct {
    int16_t ax, ay, az; /* mg, 16 g scale                              */
    int16_t gx, gy, gz; /* mdps, 2000 dps scale                        */
} imu_block_t;

/* ------------------------------------------------------------------ */
/* Global state                                                        */
/* ------------------------------------------------------------------ */
static volatile bool  g_stream_enabled = false;
static volatile bool  g_raw_optin      = false;  /* privacy default: off */
static uint8_t        g_seq[4]         = {0, 0, 0, 0};
static eeg_block_t    g_eeg;
static ppg_block_t    g_ppg;
static imu_block_t    g_imu;
static uint16_t       g_soc_percent    = 100;    /* state of charge    */

/* ------------------------------------------------------------------ */
/* CRC16-CCITT (FALSE) — used for packet integrity                      */
/* ------------------------------------------------------------------ */
static uint16_t crc16(const uint8_t *data, size_t len) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < len; i++) {
        crc ^= (uint16_t)data[i] << 8;
        for (int b = 0; b < 8; b++) {
            crc = (crc & 0x8000) ? (uint16_t)((crc << 1) ^ 0x1021) : (uint16_t)(crc << 1);
        }
    }
    return crc;
}

/* ------------------------------------------------------------------ */
/* Packet builder — packs one 20-byte GATT notify frame                */
/* ------------------------------------------------------------------ */
static void build_packet(uint8_t *out, uint8_t type, uint8_t flags,
                         const uint8_t *payload, uint8_t payload_len,
                         uint16_t sample_idx) {
    out[0] = PKT_SYNC;
    out[1] = g_seq[type]++;
    out[2] = type;
    out[3] = flags;
    memset(&out[4], 0, 14);
    memcpy(&out[4], payload, payload_len > 14 ? 14 : payload_len);
    out[16] = (uint8_t)(sample_idx & 0xFF);
    out[17] = (uint8_t)((sample_idx >> 8) & 0xFF);
    uint16_t crc = crc16(out, 18);
    out[18] = (uint8_t)(crc & 0xFF);
    out[19] = (uint8_t)(crc >> 8);
}

/* ------------------------------------------------------------------ */
/* BLE layer (HAL stubs — map to vendor SDK notify calls)              */
/* ------------------------------------------------------------------ */
static void ble_notify(uint8_t char_idx, const uint8_t *data, uint8_t len) {
    /* char_idx: 0=eeg_stream 1=ppg_stream 2=imu_stream 3=battery      */
    (void)char_idx; (void)data; (void)len;
    /* e.g. sd_ble_gatts_hvx(conn_handle, &hvx_params);               */
}

static void ble_set_advertising(bool on) {
    /* Enable connectable advertising @ 100 ms interval                */
    (void)on;
}

static void ble_handle_command(uint8_t code, const uint8_t *payload, uint8_t len) {
    switch (code) {
        case 0x01: g_stream_enabled = true;                    break; /* START */
        case 0x02: g_stream_enabled = false;                   break; /* STOP  */
        case 0x03: /* SET_RATE — v1 fixed rates; parsed but unused */  break;
        case 0x04: /* ENABLE_RAW — opt-in, resets each power cycle */
            if (len >= 1) g_raw_optin = (payload[0] != 0);
            break;
        case 0x05: /* LED_TEST */
            digital_write(PIN_LED_CYAN, len >= 1 && payload[0]);
            break;
        default: break;
    }
}

/* ------------------------------------------------------------------ */
/* Sensor HAL stubs (replace with vendor drivers)                      */
/* ------------------------------------------------------------------ */
static void ads1299_init(void) {
    /* SPI 10 MHz, 4 channels, gain 24, SR 500 SPS, RLD enabled.      */
    /* DRDY falling edge → eeg_isr().                                  */
}

static void max30102_init(void) {
    /* I2C 0x57, IR+RED LEDs, 18-bit, 100 SPS FIFO polling.           */
}

static void bmi270_init(void) {
    /* I2C 0x68, accel+gyro 200 SPS, low-power, INT1 data-ready.      */
}

static void read_eeg_block(eeg_block_t *b) {
    /* Drain 25 DRDY samples; run band-power PSD on-device.            */
    (void)b;
    /* Replace with: welch_psd_4ch(...) → fixed-point bands            */
}

static void read_ppg_block(ppg_block_t *b) {
    /* Average 5 FIFO samples; update HR/HRV/SpO2 windows.             */
    (void)b;
}

static void read_imu_block(imu_block_t *b) {
    /* Read 8 accel/gyro samples from BMI270 FIFO.                     */
    (void)b;
}

static uint8_t read_battery(void) {
    /* Fuel gauge → percent (2.5 W Qi / USB-C charge path).            */
    return g_soc_percent;
}

/* ------------------------------------------------------------------ */
/* GPIO / clock helpers (Arduino-compatible stubs)                     */
/* ------------------------------------------------------------------ */
static void pin_mode(uint8_t pin, uint8_t mode)        { (void)pin; (void)mode; }
static void digital_write(uint8_t pin, bool level)     { (void)pin; (void)level; }
static uint32_t millis(void)                           { return 0; }
static void delay_ms(uint32_t ms)                      { (void)ms; }

/* ------------------------------------------------------------------ */
/* Interrupt service routines                                          */
/* ------------------------------------------------------------------ */
static void eeg_isr(void)   { /* DRDY: latch sample into block buffer */ }
static void imu_isr(void)   { /* INT1: latch accel/gyro sample        */ }
static void ppg_isr(void)   { /* FIFO almost-full: drain              */ }

/* ------------------------------------------------------------------ */
/* Power management hooks                                              */
/* ------------------------------------------------------------------ */
static void power_sleep_until_next_block(void) {
    /* __WFE() / Zephyr pm_state_force(): sleep between 2 ms ticks.    */
    /* Radio + sensors stay in low-power while asleep.                 */
}

static void power_enter_deep_sleep(void) {
    /* 30-day standby: RTC wake on IMU motion or touch.                */
    /* Requires explicit host wake (command char) to resume streaming. */
}

/* ------------------------------------------------------------------ */
/* Main loop                                                           */
/* ------------------------------------------------------------------ */
int main(void) {
    /* --- bring-up -------------------------------------------------- */
    pin_mode(PIN_LED_CYAN, 1); pin_mode(PIN_LED_MINT, 1);
    pin_mode(PIN_DRDY_EEG, 0); pin_mode(PIN_INT_IMU, 0); pin_mode(PIN_INT_PPG, 0);

    ads1299_init();      /* EEG AFE: SPI, 4 ch, 500 SPS               */
    max30102_init();     /* PPG: I2C, 100 SPS                         */
    bmi270_init();       /* IMU: I2C, accel+gyro 200 SPS              */

    ble_set_advertising(true);
    g_stream_enabled = true;
    g_raw_optin      = false;  /* privacy-first default                */

    uint16_t tick = 0;

    while (1) {
        /* 2 ms master tick → 500 SPS scheduler                        */
        tick++;

        if (!g_stream_enabled) {
            power_sleep_until_next_block();
            continue;
        }

        /* EEG: one 25-sample block every 50 ms → 20 Hz notify         */
        if (tick % 25 == 0) {
            read_eeg_block(&g_eeg);
            uint8_t p[14];
            p[0] = (uint8_t)(g_eeg.theta_q >> 8); p[1] = (uint8_t)g_eeg.theta_q;
            p[2] = (uint8_t)(g_eeg.alpha_q >> 8); p[3] = (uint8_t)g_eeg.alpha_q;
            p[4] = (uint8_t)(g_eeg.beta_q  >> 8); p[5] = (uint8_t)g_eeg.beta_q;
            p[6] = (uint8_t)(g_eeg.gamma_q >> 8); p[7] = (uint8_t)g_eeg.gamma_q;
            p[8]  = g_eeg.blink_count;
            p[9]  = g_eeg.quality;
            p[10] = (uint8_t)(g_eeg.rms_uv & 0xFF);
            p[11] = (uint8_t)(g_eeg.rms_uv >> 8);
            p[12] = 0; p[13] = 0;                 /* reserved           */
            uint8_t pkt[PKT_SIZE];
            build_packet(pkt, TYPE_EEG,
                         g_raw_optin ? FLAG_RAW | FLAG_BLOCK_END : FLAG_BLOCK_END,
                         p, sizeof(p), tick / 25);
            ble_notify(0, pkt, PKT_SIZE);
        }

        /* PPG: one 5-sample block every 50 ms → 20 Hz notify          */
        if (tick % 25 == 0) {
            read_ppg_block(&g_ppg);
            uint8_t p[14];
            p[0] = (uint8_t)(g_ppg.hr_bpm & 0xFF);     p[1] = (uint8_t)(g_ppg.hr_bpm >> 8);
            p[2] = (uint8_t)(g_ppg.hrv_ms & 0xFF);     p[3] = (uint8_t)(g_ppg.hrv_ms >> 8);
            p[4] = (uint8_t)(g_ppg.spo2 & 0xFF);       p[5] = (uint8_t)(g_ppg.spo2 >> 8);
            p[6] = (uint8_t)(g_ppg.ir_baseline & 0xFF);
            p[7] = (uint8_t)((g_ppg.ir_baseline >> 8) & 0xFF);
            p[8] = (uint8_t)((g_ppg.ir_baseline >> 16) & 0xFF);
            p[9] = (uint8_t)((g_ppg.ir_baseline >> 24) & 0xFF);
            p[10] = g_ppg.confidence;
            p[11] = g_ppg.quality;
            p[12] = 0; p[13] = 0;
            uint8_t pkt[PKT_SIZE];
            build_packet(pkt, TYPE_PPG, FLAG_BLOCK_END, p, sizeof(p), tick / 25);
            ble_notify(1, pkt, PKT_SIZE);
        }

        /* IMU: one 8-sample block every 40 ms → 25 Hz notify          */
        if (tick % 20 == 0) {
            read_imu_block(&g_imu);
            uint8_t p[14];
            p[0] = (uint8_t)(g_imu.ax & 0xFF);  p[1] = (uint8_t)((uint16_t)g_imu.ax >> 8);
            p[2] = (uint8_t)(g_imu.ay & 0xFF);  p[3] = (uint8_t)((uint16_t)g_imu.ay >> 8);
            p[4] = (uint8_t)(g_imu.az & 0xFF);  p[5] = (uint8_t)((uint16_t)g_imu.az >> 8);
            p[6] = (uint8_t)(g_imu.gx & 0xFF);  p[7] = (uint8_t)((uint16_t)g_imu.gx >> 8);
            p[8] = (uint8_t)(g_imu.gy & 0xFF);  p[9] = (uint8_t)((uint16_t)g_imu.gy >> 8);
            p[10] = (uint8_t)(g_imu.gz & 0xFF); p[11] = (uint8_t)((uint16_t)g_imu.gz >> 8);
            p[12] = 0; p[13] = 0;
            uint8_t pkt[PKT_SIZE];
            build_packet(pkt, TYPE_IMU, FLAG_BLOCK_END, p, sizeof(p), tick / 20);
            ble_notify(2, pkt, PKT_SIZE);
        }

        /* Battery: notify on SOC change only (avoid radio spam)       */
        uint8_t soc = read_battery();
        if (soc != g_soc_percent) {
            g_soc_percent = soc;
            uint8_t b[3] = { soc, 0, 0 };   /* SOC %, mV reserved      */
            ble_notify(3, b, sizeof(b));
        }

        /* Low-battery emergency: < 5 % → drop to power-save mode      */
        if (g_soc_percent < 5) {
            g_stream_enabled = false;
            ble_set_advertising(false);
            power_enter_deep_sleep();
        }

        power_sleep_until_next_block();
    }
    return 0;
}

/*
 * End of firmware/main.c
 * Next steps (production): vendor SDK BLE stack wiring, real sensor
 * register drivers, Zephyr pm integration, MCUboot DFU slot A/B.
 */
