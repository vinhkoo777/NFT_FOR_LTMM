// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v4.9.3/contracts/token/ERC721/IERC721.sol";
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v4.9.3/contracts/security/ReentrancyGuard.sol";

contract Marketplace is ReentrancyGuard {
    struct Listing {
        address nft;
        uint256 tokenId;
        address seller;
        uint256 price;
        bool active;
    }

    mapping(address => mapping(uint256 => Listing)) public listings;

    event Listed(address indexed nft, uint256 indexed tokenId, address indexed seller, uint256 price);
    event Unlisted(address indexed nft, uint256 indexed tokenId);
    event Bought(address indexed nft, uint256 indexed tokenId, address indexed buyer, uint256 price);

    function list(address nft, uint256 tokenId, uint256 price) external {
        require(price > 0, "Price=0");
        IERC721 token = IERC721(nft);
        require(token.ownerOf(tokenId) == msg.sender, "Not owner");
        require(token.getApproved(tokenId) == address(this), "Approve first");

        listings[nft][tokenId] = Listing({
            nft: nft,
            tokenId: tokenId,
            seller: msg.sender,
            price: price,
            active: true
        });

        emit Listed(nft, tokenId, msg.sender, price);
    }

    function unlist(address nft, uint256 tokenId) external {
        Listing storage l = listings[nft][tokenId];
        require(l.active, "Not listed");
        require(l.seller == msg.sender, "Not seller");
        l.active = false;
        emit Unlisted(nft, tokenId);
    }

    function buy(address nft, uint256 tokenId) external payable nonReentrant {
        Listing storage l = listings[nft][tokenId];
        require(l.active, "Not listed");
        require(msg.value == l.price, "Wrong price");

        l.active = false;
        (bool ok, ) = payable(l.seller).call{value: msg.value}("");
        require(ok, "Pay fail");

        IERC721(nft).safeTransferFrom(l.seller, msg.sender, tokenId);

        emit Bought(nft, tokenId, msg.sender, l.price);
    }

    function getListing(address nft, uint256 tokenId)
        external
        view
        returns (address, uint256, address, uint256, bool)
    {
        Listing memory l = listings[nft][tokenId];
        return (l.nft, l.tokenId, l.seller, l.price, l.active);
    }
}
