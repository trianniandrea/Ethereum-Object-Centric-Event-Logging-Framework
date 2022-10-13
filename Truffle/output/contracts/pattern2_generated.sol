// SPDX-License-Identifier: CC-BY-SA-4.0

pragma solidity >=0.8.10;

import "./Contract.sol";

contract wrapper is Contract {

	Contract inner_contract; 

	event call_request_to_buy(Order par0);
	event call_grant_loan(Loan par0);
	event call_add_car();

	constructor (address add) {
		inner_contract = Contract(add); 
	}

	function request_to_buy (string memory car_id, int256  price) public override  returns (Order memory o){
		inner_contract.request_to_buy (car_id, price);
		 // Your code goes here ..
		emit  call_request_to_buy(Order_par0);
	}

	function grant_loan (uint256  order_id, int256  amount) public override  returns (Loan memory l){
		inner_contract.grant_loan (order_id, amount);
		 // Your code goes here ..
		emit  call_grant_loan(Loan_par0);
	}

	function add_car (string memory marca, string memory modello, string memory targa) public override {
		inner_contract.add_car (marca, modello, targa);
		 // Your code goes here ..
		emit  call_add_car();
	}

}
