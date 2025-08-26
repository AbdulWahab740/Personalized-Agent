from automation.mail_send import gmail_send_message

# Re-export the function so the import in email_graph.py works
__all__ = ['gmail_send_message']
