//
//  BarcodeApiData.swift
//  ProductSurveys
//
//  Created by Sameer Dandekar on 1/24/20.
//  Copyright © 2020 Sameer Dandekar. All rights reserved.
//
 
import Foundation
import SwiftUI

// Declare productFound as a global mutable variable accessible in all Swift files
var productFound = Product(id: UUID(), barcode_number: "", product_name: "", manufacturer: "", description: "", images: [String](), stores: [Store]())

 
// fileprivate var previousCategory = "", previousQuery = ""
 
/*
====================================
MARK: - Obtain Product Data from API
====================================
*/
public func obtainBarcodeApiData(UPC: String) {
    
//    var storesList: [Store]
   
/*     Avoid executing this function if already done for the same category and query
    if category == previousCategory && query == previousQuery {
        return
    } else {
        previousCategory = category
        previousQuery = query
    }
*/
    // Initialization
    productFound = Product(id: UUID(), barcode_number: "", product_name: "", manufacturer: "", description: "", images: [String](), stores: [Store]())
 
   
    /*
     *********************************************
     *   Obtaining API Search Query URL Struct   *
     *********************************************
     */
   
    // Replace space with UTF-8 encoding of space with %20
    
    let apiKey = "l3agpclkskpupn893ek41t0er94xvh"
    let apiUrl = "https://api.barcodelookup.com/v2/products?barcode=\(UPC)&key=\(apiKey)"
    
       
    /*
     searchQuery may include unrecognizable foreign characters inputted by the user,
     e.g., Côte d'Ivoire, that can prevent the creation of a URL struct from the
     given apiUrl string. Therefore, we must test it as an Optional.
    */
    var apiQueryUrlStruct: URL?
   
    if let urlStruct = URL(string: apiUrl) {
        apiQueryUrlStruct = urlStruct
    } else {
        // productFound will have the initial values set as above
        return
    }
 
    /*
    *******************************
    *   HTTP GET Request Set Up   *
    *******************************
    */
   
    let headers = [
        "accept": "application/json",
        "cache-control": "no-cache",
        "connection": "keep-alive",
        "host": "api.barcodelookup.com"
    ]
 
    let request = NSMutableURLRequest(url: apiQueryUrlStruct!,
                                      cachePolicy: .useProtocolCachePolicy,
                                      timeoutInterval: 10.0)
 
    request.httpMethod = "GET"
    request.allHTTPHeaderFields = headers
 
    /*
    *********************************************************************
    *  Setting Up a URL Session to Fetch the JSON File from the API     *
    *  in an Asynchronous Manner and Processing the Received JSON File  *
    *********************************************************************
    */
   
    /*
     Create a semaphore to control getting and processing API data.
     signal() -> Int    Signals (increments) a semaphore.
     wait()             Waits for, or decrements, a semaphore.
     */
    let semaphore = DispatchSemaphore(value: 0)
 
    URLSession.shared.dataTask(with: request as URLRequest, completionHandler: { (data, response, error) -> Void in
        /*
        URLSession is established and the JSON file from the API is set to be fetched
        in an asynchronous manner. After the file is fetched, data, response, error
        are returned as the input parameter values of this Completion Handler Closure.
        */
 
        // Process input parameter 'error'
        guard error == nil else {
            // productFound will have the initial values set as above
            semaphore.signal()
            return
        }
       
        /*
         ---------------------------------------------------------
         🔴 Any 'return' used within the completionHandler Closure
            exits the Closure; not the public function it is in.
         ---------------------------------------------------------
         */
 
        // Process input parameter 'response'. HTTP response status codes from 200 to 299 indicate success.
        guard let httpResponse = response as? HTTPURLResponse, (200...299).contains(httpResponse.statusCode) else {
            // productFound will have the initial values set as above
            semaphore.signal()
            return
        }
 
        // Process input parameter 'data'. Unwrap Optional 'data' if it has a value.
        guard let jsonDataFromApi = data else {
            // productFound will have the initial values set as above
            semaphore.signal()
            return
        }
 
        //------------------------------------------------
        // JSON data is obtained from the API. Process it.
        //------------------------------------------------
        do {
                   /*
                    Foundation framework’s JSONSerialization class is used to convert JSON data
                    into Swift data types such as Dictionary, Array, String, Number, or Bool.
                    */
               let jsonResponse = try JSONSerialization.jsonObject(with: jsonDataFromApi,
                                      options: JSONSerialization.ReadingOptions.mutableContainers)
        
                if let jsonObject = jsonResponse as? [String: Any] {
                      
                    guard let productsDictionary = jsonObject["products"] as? [Any] else {
                        
                        semaphore.signal()
                        return }

                    guard let productDictionary = productsDictionary[0] as? [String: Any] else {
                        semaphore.signal()
                        return }

                    guard let barcodeNumber = productDictionary["barcode_number"] as? String else { return }
                    
                    guard let productName = productDictionary["product_name"] as? String else { return }
                    
                    guard let productManufacturer = productDictionary["manufacturer"] as? String else {return}
                       
                    guard let productDescription = productDictionary["description"] as? String else {return}
                       
                    guard let imageList = productDictionary["images"] as? [String] else { return }
                    
                    guard let storesDictionary = productDictionary["stores"] as? [Any] else {
                        
                        semaphore.signal()
                        return }
                    
                    // get stores
                    var storesList = [Store]()
                    for (element) in storesDictionary {
                        guard let store = element as? [String: Any] else {
                            semaphore.signal()
                            return }
                        
                        guard let storeName = store["store_name"] as? String else {
                            semaphore.signal()
                            return }
    
                        guard let storePrice = store["store_price"] as? String else {
                            semaphore.signal()
                            return }
                        
                        guard let productUrl = store["product_url"] as? String else {
                            semaphore.signal()
                            return }
                        
                        guard let currencyCode = store["currency_code"] as? String else {
                            semaphore.signal()
                            return }
                        
                        let currencySymbol = store["currency_symbol"] as? String
                        
                        let storeFound = Store(id: UUID(), store_name: storeName, store_price: storePrice, product_url: productUrl, currency_code: currencyCode, currency_symbol: currencySymbol ?? "")
                        
                        storesList.append(storeFound)
                    }


                    productFound = Product(id: UUID(), barcode_number: barcodeNumber, product_name: productName, manufacturer: productManufacturer, description: productDescription, images: imageList, stores: storesList)
                                   
    
                   } else {
                    
                        semaphore.signal()
                        return }
                  
                      
        
               } catch {
            semaphore.signal()
            return
        }
 
        semaphore.signal()
    }).resume()
 
    /*
     The URLSession task above is set up. It begins in a suspended state.
     The resume() method starts processing the task in an execution thread.
 
     The semaphore.wait blocks the execution thread and starts waiting.
     Upon completion of the task, the Completion Handler code is executed.
     The waiting ends when .signal() fires or timeout period of 10 seconds expires.
    */
 
    _ = semaphore.wait(timeout: .now() + 10)
 
}
 
