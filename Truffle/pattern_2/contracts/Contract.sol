// SPDX-License-Identifier: CC-BY-SA-4.0
pragma solidity >=0.7.0 <0.9.0;


contract Contract {

    struct Car
    {
        string id; //targa
        string marca;
        string modello;
    }

    struct Order
    {
        uint256 id;
        string[] Car_id;
        uint256[] Loan_id;
        int price;
    }

    struct Loan
    {
        uint256 id;
        uint256[] Order_id;
        int amount;
    }

    mapping(string => Car) public cars;
    Order[] public orders;
    Loan[] public loans;


    function request_to_buy(string memory car_id, int price) public virtual returns (Order memory o)
    {
        Order memory order;
        order.id=orders.length;
        order.price = price;

        orders.push(order);
        orders[order.id].Car_id.push(car_id);
        return orders[order.id];
    }

    function grant_loan(uint256 order_id, int amount) public virtual returns (Loan memory l)
    {
        Loan memory loan;
        loan.id = loans.length;
        loan.amount = amount;
        orders[order_id].Loan_id.push(loans.length);

        loans.push(loan);
        loans[loan.id].Order_id.push(order_id);
        return loans[loan.id];
    }


    function add_car(string memory marca, string memory modello, string memory targa) public
    {
        Car memory car;
        car.modello = modello;
        car.marca = marca;
        car.id = targa;

        cars[targa] = car;
    }


}




contract Wrapper is Contract {

	Contract inner_contract; 

	event call_request_to_buy(Order par0);
	event call_grant_loan(Loan par0);
    event updatefk_car(Car c);

	constructor (address add) {
		inner_contract = Contract(add); 
	}

	function request_to_buy (string memory car_id, int256  price) override public returns (Order memory o){
		o = inner_contract.request_to_buy (car_id, price);
		emit  call_request_to_buy(o);

        for (uint i = 0; i < o.Car_id.length; i++) { 
            Car memory c;
            (c.id,c.marca, c.modello) = inner_contract.cars(o.Car_id[i]);
            emit updatefk_car(c);
        }
	}

	function grant_loan (uint256 order_id, int256  amount) override public  returns (Loan memory l){
		l = inner_contract.grant_loan (order_id, amount);
		emit  call_grant_loan(l);
	}

}
