from database import session, Companhia, engine, Base

def resetar_e_configurar():
    print("--- Iniciando Configuração do Sistema ---")
    
    try:
        # 1. Deleta todas as tabelas antigas para evitar erros de colunas faltando
        Base.metadata.drop_all(engine)
        print("✅ Banco de dados antigo removido.")

        # 2. Cria as tabelas do zero com a estrutura nova
        Base.metadata.create_all(engine)
        print("✅ Nova estrutura de tabelas criada.")

        # 3. Lista de operadoras atualizada
        operadoras = [
            "Amil", 
            "Bradesco", 
            "SulAmérica", 
            "Unimed", 
            "Hapvida"
        ]
        
        # 4. Loop para cadastrar cada uma no banco
        for nome_op in operadoras:
            nova_cia = Companhia(nome=nome_op)
            session.add(nova_cia)
        
        # 5. Salva as alterações definitivamente
        session.commit()
        print(f"✅ Sucesso! {len(operadoras)} operadoras cadastradas.")
        print("\nAgora você já pode rodar o: streamlit run app.py")

    except Exception as e:
        print(f"❌ Ocorreu um erro ao configurar: {e}")
        session.rollback()

if __name__ == "__main__":
    resetar_e_configurar()