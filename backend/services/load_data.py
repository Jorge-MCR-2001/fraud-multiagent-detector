import pandas as pd

from settings.paths import TRANSACTIONS_DIR, CUSTOMER_BEHIVOR_DIR


transactions = pd.read_csv(TRANSACTIONS_DIR)
customer_behivor = pd.read_csv(CUSTOMER_BEHIVOR_DIR)

def get_transactions(transaction_id):

    # Busqueda de la transacción en base a el ID
    result = transactions[
        transactions["transaction_id"] == transaction_id
    ]
    
    if result.empty: # Si y solo no se encontro una fila mediante el ID ingresado
        return None

    # Convertir el output_query a formato json
    return result.iloc[0].to_dict()

def get_customer_behivor(customer_id):
    
    # Busqueda de la transacción en base a el ID
    result = customer_behivor[
        customer_behivor["customer_id"] == customer_id
    ]
    
    if result.empty: # Si y solo no se encontro una fila mediante el ID ingresado
        return None

    # Convertir el output_query a formato json
    return result.iloc[0].to_dict()
