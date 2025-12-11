- [ ] Add feature to detect the house rent transaction, that comes with no description, only with 'Pagamento de Boleto' as the 'Lançamento' column value
- [ ] Fix builder#generate_references. If the target references table doesn't already exists an error
happens. The problem can be in the client#ensure_worksheet 