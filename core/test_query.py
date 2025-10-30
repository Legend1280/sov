from reasoner import get_reasoner

reasoner = get_reasoner("./core.db", "./ontology")

print("Testing query...")
try:
    transactions = reasoner.query("Transaction", limit=5)
    print(f"Found {len(transactions)} transactions")
    for t in transactions:
        print(f"- {t['symbolic']['id']}: {t['object']}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
