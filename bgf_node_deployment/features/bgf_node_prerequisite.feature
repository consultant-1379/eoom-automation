Feature: BGF NODE PRE-REQUISITES ON EO-CM



  Scenario: Get VNFD ID from ECM host blade server
    Given I start the Scenario to Get VNFD ID from ECM host blade server


  Scenario: Transfer the BGF software from HOST blade to VNF-LCM
    Given I start the Scenario to Copy the BGF software from HOST blade to VNF-LCM


  Scenario: Generate ssh keys using JBOSS user
    Given I start the Scenario to Generate ssh keys using JBOSS user

    
  Scenario: Onboard Network stack for BGF Node
    Given I start the Scenario to Onboard Network Stack for BGF node
    
  
  Scenario: Deploy Network stack for BGF Node
    Given I start the Scenario to Deploy Network Stack for BGF node