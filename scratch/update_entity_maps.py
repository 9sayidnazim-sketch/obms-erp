files = [
    '/Users/ceooctapus/mehar/api/[...path].js',
    '/Users/ceooctapus/mehar/api/entities/[...entity].js',
    '/Users/ceooctapus/mehar/src/api/supabaseAdapter.js'
]

for file_path in files:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        target = "AppNotification: 'app_notifications',"
        replacement = "AppNotification: 'app_notifications',\n  StaffInvitation: 'staff_invitations',"
        
        if "StaffInvitation:" not in content and target in content:
            new_content = content.replace(target, replacement, 1)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f'Updated {file_path}')
        else:
            print(f'Already updated or target not found in {file_path}')
    except Exception as e:
        print(f'Error processing {file_path}: {e}')
