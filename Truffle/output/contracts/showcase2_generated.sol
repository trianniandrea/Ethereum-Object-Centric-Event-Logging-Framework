// SPDX-License-Identifier: CC-BY-SA-4.0

pragma solidity >=0.8.10;

import "./Decoupled.sol";

contract showcase2_generated is Business {

	Contract inner_contract; 

	event call_add_flight();
	event call_add_traveller();
	event call_add_luggage();
	event call_buy_trip();
	event call_check_in();
	event call_deliver_luggage();
	event call_security_controls();
	event call_start_flight();
	event call_cancel_flight();

	constructor (address add) {
		inner_contract = Contract(add); 
	}

	function add_flight (string memory from, string memory to, uint256  time_departure, uint256  time_arrival, string memory company) public override {
		inner_contract.add_flight (from, to, time_departure, time_arrival, company);
		 // Your code goes here ..
		emit  call_add_flight();
	}

	function add_traveller (string memory name, string memory surname, string memory nationality) public override {
		inner_contract.add_traveller (name, surname, nationality);
		 // Your code goes here ..
		emit  call_add_traveller();
	}

	function add_luggage (string memory color, uint64  weight, address  traveller_id) public override {
		inner_contract.add_luggage (color, weight, traveller_id);
		 // Your code goes here ..
		emit  call_add_luggage();
	}

	function buy_trip (string[] memory class, string[] memory seat, address[] memory travellers) public override  returns (Ticket[] memory t){
		inner_contract.buy_trip (class, seat, travellers);
		 // Your code goes here ..
		emit  call_buy_trip();
	}

	function check_in (uint256[] memory t, uint64  gate, uint256  boarding_time, address  Traveller_id, uint256  flight_id) public override  returns (boarding_card memory c){
		inner_contract.check_in (t, gate, boarding_time, Traveller_id, flight_id);
		 // Your code goes here ..
		emit  call_check_in();
	}

	function deliver_luggage (uint256  card_id, uint256[] memory luggages) public override  returns (boarding_card memory c){
		inner_contract.deliver_luggage (card_id, luggages);
		 // Your code goes here ..
		emit  call_deliver_luggage();
	}

	function security_controls (uint256  card_id) public override  returns (boarding_card memory c){
		inner_contract.security_controls (card_id);
		 // Your code goes here ..
		emit  call_security_controls();
	}

	function start_flight (uint256  flight_id) public override  returns (flight memory f){
		inner_contract.start_flight (flight_id);
		 // Your code goes here ..
		emit  call_start_flight();
	}

	function cancel_flight (uint256  flight_id) public override  returns (flight memory f){
		inner_contract.cancel_flight (flight_id);
		 // Your code goes here ..
		emit  call_cancel_flight();
	}

}
