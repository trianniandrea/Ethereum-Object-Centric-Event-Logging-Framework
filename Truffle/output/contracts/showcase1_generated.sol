// SPDX-License-Identifier: CC-BY-SA-4.0

pragma solidity >=0.8.10;

import "./Decoupled.sol";

contract showcase1_generated is Business {

	Contract inner_contract; 

	event call_SignUP();
	event call_addProduct();
	event call_deliveryItems();
	event call_Create_Order();
	event call_add_orderline();
	event call_pick_item();
	event call_wrap_item();

	constructor (address add) {
		inner_contract = Contract(add); 
	}

	function SignUP (string memory name) public override {
		inner_contract.SignUP (name);
		 // Your code goes here ..
		emit  call_SignUP();
	}

	function addProduct (string memory name, uint256  price, string[] memory colori) public override {
		inner_contract.addProduct (name, price, colori);
		 // Your code goes here ..
		emit  call_addProduct();
	}

	function deliveryItems (uint256  ol_id, address  cust, string memory add) public override  returns (Delivery memory del){
		inner_contract.deliveryItems (ol_id, cust, add);
		 // Your code goes here ..
		emit  call_deliveryItems();
	}

	function Create_Order (address  customer, string memory referreal) public override  returns (Order memory order){
		inner_contract.Create_Order (customer, referreal);
		 // Your code goes here ..
		emit  call_Create_Order();
	}

	function add_orderline (uint256  order_id, Product memory prod, uint256  qty) public override {
		inner_contract.add_orderline (order_id, prod, qty);
		 // Your code goes here ..
		emit  call_add_orderline();
	}

	function pick_item (uint256  ol_id) public override  returns (OrderLine memory ol){
		inner_contract.pick_item (ol_id);
		 // Your code goes here ..
		emit  call_pick_item();
	}

	function wrap_item (uint256  ol_id, string[] memory notes) public override  returns (OrderLine memory ol){
		inner_contract.wrap_item (ol_id, notes);
		 // Your code goes here ..
		emit  call_wrap_item();
	}

}
