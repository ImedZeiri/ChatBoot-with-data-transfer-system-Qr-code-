package com.customer.cms.api;

import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;



@RestController
public class Hello {

    @RequestMapping(value="/Hello")
    public String sayHello(){
        return "Hello World";
    }



    @RequestMapping(value ="/imed")
    public String seven(){
        return "<h1><br>Bonjour monsieur Imed</br></h1>";
    }



    @RequestMapping(value = "Test")
    public int sum(){
        return 123+354;
    }


}
