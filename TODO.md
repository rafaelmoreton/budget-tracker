- [ ] Add feature to detect the house rent transaction, that comes with no description, only with 'Pagamento de Boleto' as the 'Lançamento' column value
- [x] Fix builder#generate_references. If the target references table doesn't already exists an error
happens. The problem can be in the client#ensure_worksheet 
- [ ] Add timestamp to generated statement transactions parsed and exported to csv, to be able to generate more files and keep track of them
- [ ] Find out why the BB Credit Card parsed and calculated total is a little different from the extracted total