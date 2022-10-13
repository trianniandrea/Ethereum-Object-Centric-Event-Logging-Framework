// SPDX-License-Identifier: CC-BY-SA-4.0
pragma solidity >=0.7.0 <0.9.0;

// Business Logic inside this showcase contract


interface ContractInterface 
{
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

    function request_to_buy(string memory car_id, int price) external returns (Order memory o);
    function grant_loan(uint256 order_id, int amount) external returns (Loan memory l);
}




contract Contract is ContractInterface{

    mapping(string => Car) public cars;
    Order[] public orders;
    Loan[] public loans;


    function request_to_buy(string memory car_id, int price) external returns (Order memory o)
    {
        Order memory order;
        order.id=orders.length;
        order.price = price;

        orders.push(order);
        orders[order.id].Car_id.push(car_id);
        return orders[order.id];
    }

    function grant_loan(uint256 order_id, int amount) external returns (Loan memory l)
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