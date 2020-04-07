//
//  WebRequestData.swift
//  FootballTickets
//
//  Created by Sameer Dandekar on 1/24/20.
//  Copyright © 2020 Sameer Dandekar. All rights reserved.
//
 
import Foundation
import SwiftUI
 
// fileprivate var previousCategory = "", previousQuery = ""
 
/*
====================================
MARK: - GET Request Data from API
====================================
*/
public func getRequestData() {
    
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

/*
====================================
MARK: - POST Request Data from API
====================================
*/
public func postRequestData(user: String, action: String) {
    // prepare json data
    let json: [String: Any] = ["user": "sameer", "action": "user_balance"]
    let jsonData = try? JSONSerialization.data(withJSONObject: json)

    // create post request
    let url = URL(string: "http://goblins.info.tm/requests.pyhtml")!
    var request = URLRequest(url: url)
    request.httpMethod = "POST"

    // insert json data to the request
    request.httpBody = jsonData

    let task = URLSession.shared.dataTask(with: request) { data, response, error in
        guard let data = data, error == nil else {
            print(error?.localizedDescription ?? "No data")
            return
        }
        let responseJSON = try? JSONSerialization.jsonObject(with: data, options: [])
        // print if response is JSON object
        if let responseJSON = responseJSON as? [String: Any] {
            print(responseJSON)
        }
    }

    task.resume()
}
 
