from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import json

app = Flask(__name__)
app.secret_key = "contact_management_professional_2024"

# Linked list node
class ContactNode:
    def __init__(self, name, phone, email="", address=""):
        self.name = name.strip().title()
        self.phone = phone.strip()
        self.email = email.strip().lower()
        self.address = address.strip()
        self.next = None
    
    def to_dict(self):
        return {
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'address': self.address
        }

class ContactLinkedList:
    def __init__(self):
        self.head = None
        self.size = 0
    
    def add_contact(self, name, phone, email="", address=""):
        if not name or not phone:
            return False, "Name and phone are required"
        if self._contact_exists(name):
            return False, "Contact already exists"
        import re
        clean_phone = re.sub(r'[^\d]', '', phone)
        if not (10 <= len(clean_phone) <= 15):
            return False, "Invalid phone number format"
        if email:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                return False, "Invalid email format"
        new_node = ContactNode(name, phone, email, address)
        new_node.next = self.head
        self.head = new_node
        self.size += 1
        return True, "Contact added successfully"
    
    def delete_contact(self, name):
        if not self.head:
            return False, "No contacts to delete"
        if self.head.name.lower() == name.lower():
            self.head = self.head.next
            self.size -= 1
            return True, "Contact deleted successfully"
        current = self.head
        while current.next:
            if current.next.name.lower() == name.lower():
                current.next = current.next.next
                self.size -= 1
                return True, "Contact deleted successfully"
            current = current.next
        return False, "Contact not found"
    
    def search_contacts(self, query):
        results = []
        current = self.head
        query_lower = query.lower()
        while current:
            if (query_lower in current.name.lower() or 
                query_lower in current.phone or 
                query_lower in current.email.lower() or
                query_lower in current.address.lower()):
                results.append(current.to_dict())
            current = current.next
        return results
    
    def get_all_contacts(self):
        contacts = []
        current = self.head
        while current:
            contacts.append(current.to_dict())
            current = current.next
        return contacts
    
    def update_contact(self, name, phone=None, email=None, address=None):
        current = self.head
        while current:
            if current.name.lower() == name.lower():
                if phone:
                    import re
                    clean_phone = re.sub(r'[^\d]', '', phone)
                    if 10 <= len(clean_phone) <= 15:
                        current.phone = phone.strip()
                    else:
                        return False, "Invalid phone number format"
                if email is not None:
                    if email:
                        import re
                        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                        if re.match(email_pattern, email):
                            current.email = email.strip().lower()
                        else:
                            return False, "Invalid email format"
                    else:
                        current.email = ""
                if address is not None:
                    current.address = address.strip()
                return True, "Contact updated successfully"
            current = current.next
        return False, "Contact not found"
    
    def _contact_exists(self, name):
        current = self.head
        while current:
            if current.name.lower() == name.lower():
                return True
            current = current.next
        return False

    def get_stats(self):
        total = self.size
        with_email = 0
        with_address = 0
        current = self.head
        while current:
            if current.email:
                with_email += 1
            if current.address:
                with_address += 1
            current = current.next
        return {
            'total': total,
            'with_email': with_email,
            'with_address': with_address
        }

# Initialize global contact list
contact_list = ContactLinkedList()

# Add sample data
sample_contacts = [
    ("John Doe", "1234567890", "john.doe@email.com", "123 Main Street, New York"),
    ("Jane Smith", "9876543210", "jane.smith@gmail.com", "456 Oak Avenue, Los Angeles"),
    ("Michael Johnson", "5555551234", "m.johnson@company.com", "789 Pine Road, Chicago"),
    ("Sarah Wilson", "7777778888", "sarah.w@outlook.com", "321 Elm Street, Houston"),
    ("David Brown", "9999994444", "david.brown@email.com", "654 Maple Drive, Phoenix")
]
for name, phone, email, address in sample_contacts:
    contact_list.add_contact(name, phone, email, address)

# Routes
@app.route('/')
def index():
    contacts = contact_list.get_all_contacts()
    stats = contact_list.get_stats()
    return render_template('index.html', contacts=contacts, stats=stats)

@app.route('/add_contact', methods=['POST'])
def add_contact():
    data = request.get_json()
    name = data.get('name', '').strip()
    phone = data.get('phone', '').strip()
    email = data.get('email', '').strip()
    address = data.get('address', '').strip()
    success, message = contact_list.add_contact(name, phone, email, address)
    return jsonify({
        'success': success,
        'message': message,
        'contact': {'name': name, 'phone': phone, 'email': email, 'address': address} if success else None,
        'stats': contact_list.get_stats()
    })

@app.route('/delete_contact', methods=['POST'])
def delete_contact():
    data = request.get_json()
    name = data.get('name', '').strip()
    success, message = contact_list.delete_contact(name)
    return jsonify({'success': success, 'message': message, 'stats': contact_list.get_stats()})

@app.route('/update_contact', methods=['POST'])
def update_contact():
    data = request.get_json()
    name = data.get('name', '').strip()
    phone = data.get('phone', '').strip() if data.get('phone') else None
    email = data.get('email', '').strip() if 'email' in data else None
    address = data.get('address', '').strip() if 'address' in data else None
    success, message = contact_list.update_contact(name, phone, email, address)
    return jsonify({'success': success, 'message': message, 'stats': contact_list.get_stats()})

@app.route('/search_contacts')
def search_contacts():
    query = request.args.get('q', '').strip()
    if not query:
        contacts = contact_list.get_all_contacts()
    else:
        contacts = contact_list.search_contacts(query)
    return jsonify({'contacts': contacts, 'count': len(contacts)})

@app.route('/get_stats')
def get_stats():
    return jsonify(contact_list.get_stats())

if __name__ == '__main__':
    app.run(debug=True)
