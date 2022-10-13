// SPDX-License-Identifier: CC-BY-SA-4.0
pragma solidity >=0.7.0 <0.9.0;


contract Monolith {

   struct Order 
   {
        uint256 id;
        uint256 date;
        uint256[] OrderLine_id;
        Customer c;
   }

    struct OrderLine
   {    
        uint256 id;
        Product p;
        uint qty;
        Delivery d;
   }

    struct Product
   {
        string name;
        uint price;
        string[] colori;
   }

    struct Customer
   {
        address id;
        string name;
   }

    struct Delivery
   {
        uint256 id;
        address Customer_id;
        uint256 date;
        string delivery_add;
   }


    event call_create_order(Order o, string referreal);
    event call_pick_item(OrderLine ol);
    event call_wrap_item(OrderLine ol, string[] notes);
    event call_delivery_items(Delivery del);
    event update_orderline(OrderLine ol);
    event update_order(Order o);

    mapping (address => Customer) public c;

    Order[] public orders;
    OrderLine[] public orderlines;
    Product[] public p;
    Delivery[] public deliveries;



    function SignUP (string memory name) public {
        c[msg.sender] = Customer(msg.sender, name);
    }

    function addProduct (string memory name, uint price, string[] memory colori) public {
        p.push(Product(name,price,colori));
    }


    function Create_Order(address customer, string memory referreal) public 
    {
        Order memory order;
        order.date = block.timestamp;
        order.c = c[customer];
        order.id = orders.length;
        orders.push(order);

        emit call_create_order(order,referreal);
    }


    function add_orderline(uint order_id, Product memory prod, uint qty) public {
        OrderLine memory ol;
        ol.qty = qty;
        ol.p = prod;
        ol.id = orderlines.length;
        orderlines.push(ol);
        orders[order_id].OrderLine_id.push(ol.id);
    }


    function pick_item (uint ol_id) public {
        emit call_pick_item(orderlines[ol_id]);

        for (uint i = 0; i < orders.length; i++) { 
            uint256[] memory ols = orders[i].OrderLine_id;
            for (uint j = 0; j <  ols.length; j++) 
            { 
                if ( ols[j] == ol_id)
                {
                    emit update_order(orders[i]);
                }
            }
        }
    }


    function wrap_item (uint ol_id, string[] memory notes) public 
    {
         emit call_wrap_item(orderlines[ol_id],notes);
    }


    function deliveryItems (uint ol_id, address cust, string memory add) public 
    {
        deliveries.push(Delivery(deliveries.length, cust, block.timestamp,add));
        orderlines[ol_id].d = deliveries[deliveries.length-1];

        emit call_delivery_items(deliveries[deliveries.length-1]);
        emit update_orderline(orderlines[ol_id]);
    }

}