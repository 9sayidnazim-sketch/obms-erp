file_path = '/Users/ceooctapus/mehar/base44/entities/Sale.jsonc'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

target = '''    "bill_sent_email": {
      "type": "boolean",
      "title": "Bill Sent (Email)",
      "default": false
    },'''

replacement = '''    "bill_sent_email": {
      "type": "boolean",
      "title": "Bill Sent (Email)",
      "default": false
    },
    "email_recipient": {
      "type": "string",
      "title": "Email Recipient"
    },
    "email_status": {
      "type": "string",
      "title": "Email Status"
    },
    "email_history": {
      "type": "array",
      "title": "Email Dispatch History",
      "items": {
        "type": "object"
      }
    },'''

if "email_history" not in content and target in content:
    new_content = content.replace(target, replacement, 1)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print('Sale.jsonc updated with email_history')
else:
    print('Sale.jsonc already has email_history or target not found')
