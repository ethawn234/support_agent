from langchain_google_community import GmailToolkit

toolkit = GmailToolkit()
tools = toolkit.get_tools()
print(tools)