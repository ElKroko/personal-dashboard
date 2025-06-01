#!/usr/bin/env python3
"""
Test the categorization API functionality to verify frontend integration
"""
import requests
import json

def test_categorization():
    print('=== Testing Categorization API ===')
    
    # First, get uncategorized transactions
    print('Fetching uncategorized transactions...')
    response = requests.get('http://localhost:8000/historial/')
    if response.status_code != 200:
        print(f'Failed to fetch transactions: {response.status_code}')
        return False
    
    data = response.json()
    uncategorized = [t for t in data if t.get('categoria') == 'Sin categorizar']
    print(f'Found {len(uncategorized)} uncategorized transactions')
    
    if not uncategorized:
        print('No uncategorized transactions found to test with')
        return False
    
    # Take the first uncategorized transaction
    transaction = uncategorized[0]
    transaction_id = transaction['id']
    description = transaction['descripcion']
    print(f'Testing with transaction ID: {transaction_id}')
    print(f'Description: {description}')
    
    # Try to categorize it
    new_category = 'Gasto - Alimentación'
    print(f'Attempting to categorize as: {new_category}')
    
    categorize_response = requests.patch(
        f'http://localhost:8000/transacciones/{transaction_id}/categoria',
        json={'nueva_categoria': new_category},
        headers={'Content-Type': 'application/json'}
    )
    
    print(f'Categorization response status: {categorize_response.status_code}')
    print(f'Categorization response: {categorize_response.json()}')
    
    if categorize_response.status_code != 200:
        print('❌ Categorization failed')
        return False
    
    # Verify the change
    print('Verifying the change...')
    verify_response = requests.get('http://localhost:8000/historial/')
    if verify_response.status_code != 200:
        print('❌ Failed to verify changes')
        return False
    
    updated_data = verify_response.json()
    updated_uncategorized = [t for t in updated_data if t.get('categoria') == 'Sin categorizar']
    print(f'Uncategorized transactions after update: {len(updated_uncategorized)}')
    
    # Find the updated transaction
    updated_transaction = next((t for t in updated_data if t['id'] == transaction_id), None)
    if updated_transaction:
        print(f'Transaction {transaction_id} category is now: {updated_transaction["categoria"]}')
        if updated_transaction['categoria'] == new_category:
            print('✅ Categorization successful!')
            return True
        else:
            print('❌ Category not updated correctly')
            return False
    else:
        print('❌ Updated transaction not found')
        return False

if __name__ == '__main__':
    success = test_categorization()
    if success:
        print('\n🎉 All tests passed! The categorization functionality is working.')
    else:
        print('\n❌ Tests failed. There may be an issue with the API.')
