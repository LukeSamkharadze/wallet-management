Table users {
  id SMALLINT [pk]
  api_key VARCHAR(45) [not null]
  name VARCHAR(45) [not null]
  create_date_utc TIMESTAMP [not null]
}


Table wallets {
  id SMALLINT [pk]
  public_key VARCHAR(45) [not null]
  create_date_utc TIMESTAMP [not null]
  btc_amount DECIMAL [not null]
  
  api_key VARCHAR(45) [not null]
}
Ref: wallets.api_key > users.api_key


Table transactions {
  id SMALLINT [pk]
  
  src_api_key VARCHAR(45) [not null]
  
  src_public_key VARCHAR(45) [not null]
  dst_public_key VARCHAR(45) [not null]
  btc_amount DECIMAL [not null]
  commission DECIMAL [not null]
  create_date_utc TIMESTAMP [not null]
}
Ref: transactions.src_public_key > wallets.public_key
Ref: transactions.dst_public_key > wallets.public_key
Ref: transactions.src_api_key > users.api_key


Table commission_sums {
  create_day_utc DATE [pk]
  commission_sum DECIMAL [not null]
  num_transactions DECIMAL [not null]
}