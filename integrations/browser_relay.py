class BrowserRelay:
    def __init__(self, cdp_endpoint: str):
        self.endpoint = cdp_endpoint
        
    def trigger_scenario(self, scenario: str):
        if scenario in ["MAX_ENTANGLEMENT", "BELL_LIKE"]:
            self.open_dashboard()
            
    def open_dashboard(self):
        print(f"Opening Sovereign Dashboard via {self.endpoint}")
