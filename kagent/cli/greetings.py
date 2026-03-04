def banner():
    green = "\033[92m"
    reset = "\033[0m"

    print(f"""{green}
██╗  ██╗    █████╗  ██████╗ ███████╗███╗   ██╗████████╗
██║ ██╔╝   ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝
█████╔╝    ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║
██╔═██╗    ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║
██║  ██╗   ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║
╚═╝  ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝

        ⚡ kagent — AI CLI Agent
        
Welcome to KAgent, the knowledge agent that can help you with various tasks.
KAgent is a locally running AI agent system designed to assist you in daily task completion.
{reset}
""")

banner()