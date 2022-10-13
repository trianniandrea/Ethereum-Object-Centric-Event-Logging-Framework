// SPDX-License-Identifier: CC-BY-SA-4.0
pragma solidity >=0.7.0 <0.9.0;

import "./Contract.sol";


contract Wrapper is ContractInterface {

	Contract inner_contract; 

	event call_request_to_buy(Order par0);
	event call_grant_loan(Loan par0);
    event updatefk_car(Car c);

	constructor (address add) {
		inner_contract = Contract(add); 
	}

	function request_to_buy (string memory car_id, int256  price) external returns (Order memory o){
		o = inner_contract.request_to_buy (car_id, price);
		emit  call_request_to_buy(o);

        for (uint i = 0; i < o.Car_id.length; i++) { 
            Car memory c;
            (c.id,c.marca, c.modello) = inner_contract.cars(o.Car_id[i]);
            emit updatefk_car(c);
        }
	}

	function grant_loan (uint256 order_id, int256  amount) external returns (Loan memory l){
		l = inner_contract.grant_loan (order_id, amount);
		emit  call_grant_loan(l);
	}

}

