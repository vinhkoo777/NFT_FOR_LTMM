# Các lưu ý 

RPC_URL=http://127.0.0.1:7545 # cái này là localhost
PRIVATE_KEY_SELLER=0xba37c42f7116a0e0f4bbaaedf2be5c6553737562405fef01f48be71ea7f2838f (private key của seller)
PRIVATE_KEY_BUYER=0x19530b4f13e0bea3dafc4027e835477a6cbc8fdc51bdaa7ad4e98853f49f6c89 (private key của buyer)
ADDR_MY_NFT=0xa3AFF651CBC28640Ed03643055711c10c6699Fb9 ( lúc mà deploy MyMFT xong )
ADDR_MARKET=0x874d1b65D5eFeAE884880B33557488f6726e0ABd ( lúc mà deploy marketplace xong xong )
CHAIN_ID=1337

# nhớ chỉnh phiên bản xuống 0.8.19 vì phiên bản này ổn định hơn 
# (  Lúc compile chỉnh xuống 0.8.19 cùng với cái pragma solidity ^0.8.19; ) với khi mà chỉnh xong và compile xong rồi thì phải copy abi remix của myNFT và Maketplace vào thư mục abi của ứng dụng 