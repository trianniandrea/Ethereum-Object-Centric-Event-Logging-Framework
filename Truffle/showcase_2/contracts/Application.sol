// SPDX-License-Identifier: CC-BY-SA-4.0
pragma solidity >=0.7.0 <0.9.0;


contract Application {

    struct Ticket{
        uint256 id;
        string class;
        string seat;
        address Traveller_id;
    }

    struct Traveller{
        address id;
        string name;
        string surname;
        string nationality;
    }

    struct Luggage{
        uint256 id;
        string color;
        uint64 weight;
        address Traveller_id;
    }

    struct boarding_card{
        uint256 id;
        uint64 gate;
        uint256 boarding_time;
        address Traveller_id;
        uint256 flight_id;
        bool luggage_delivered;
        bool security_check;
        uint256[] Luggage_id;
        uint256[] Ticket_id;
    }

    struct flight{
        uint256 id;
        string from;
        string to;
        uint256 time_departure;
        uint256 time_arrival;
        string state;
        string company; //possibile altro oggetto se serve
    }

    Ticket[] public tickets;
    boarding_card[] public cards;
    flight[] public flights;
    Luggage[] public luggages;
    mapping (address => Traveller) public travellers;

    function add_flight(string memory from, string memory to, uint256 time_departure, uint256 time_arrival, string memory company) public {
        flights.push(flight(flights.length, from, to, time_departure, time_arrival, "scheduled", company));
    }

    function add_traveller(string memory name, string memory surname, string memory nationality) public {
        travellers[msg.sender] = Traveller(msg.sender, name, surname, nationality);
    }

    function add_luggage(string memory color, uint64 weight, address traveller_id) public {
        luggages.push(Luggage(luggages.length, color, weight, traveller_id));
    }

    function buy_trip (string[] memory class, string[] memory seat, address[] memory travellers) public {
        for (uint i = 0; i < class.length; i++) { 
            tickets.push(Ticket(tickets.length, class[i], seat[i], travellers[i]));
        }
    }

    function check_in ( uint256[] memory t, uint64 gate, uint256 boarding_time, address Traveller_id, uint256 flight_id) public {
        boarding_card memory c;
        c.id = cards.length;
        c.gate = gate;
        c.boarding_time = boarding_time;
        c.Traveller_id = Traveller_id;
        c.flight_id = flight_id;
        c.Ticket_id = t;
        cards.push(c);
 
    }

    function deliver_luggage (uint256 card_id, uint256[] memory luggages) public {
        cards[card_id].luggage_delivered = true;
        cards[card_id].Luggage_id = luggages;
    }

    function security_controls (uint256 card_id) public {
        cards[card_id].security_check = true;
    }

    function start_flight (uint flight_id) public{
        flights[flight_id].state="Departed";
    }

    function cancel_flight (uint flight_id) public{
        flights[flight_id].state="Cancelled"; 
    }
}