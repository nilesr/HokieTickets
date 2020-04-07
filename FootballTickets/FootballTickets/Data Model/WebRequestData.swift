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
//var productFound = Product(id: UUID(), barcode_number: "", product_name: "", manufacturer: "", description: "", images: [String](), stores: [Store]())

 
// fileprivate var previousCategory = "", previousQuery = ""
 
/*
====================================
MARK: - Obtain Request Data from API
====================================
*/
public func obtainRequestData(user: String, action: String) {
    
    // Create URL
    let url = URL(string: "http://goblins.info.tm/requests.pyhtml")
    guard let requestUrl = url else { fatalError() }
    // Create URL Request
    var request = URLRequest(url: requestUrl)
    // Specify HTTP Method to use
    request.httpMethod = "GET"
    // Send HTTP Request
    let task = URLSession.shared.dataTask(with: request) { (data, response, error) in
        
        // Check if Error took place
        if let error = error {
            print("Error took place \(error)")
            return
        }
        
        // Read HTTP Response Status code
        if let response = response as? HTTPURLResponse {
            print("Response HTTP Status code: \(response.statusCode)")
        }
        
        // Convert HTTP Response Data to a simple String
        if let data = data, let dataString = String(data: data, encoding: .utf8) {
            print("Response data string:\n \(dataString)")
        }
        
    }
    task.resume()
 
}
 
