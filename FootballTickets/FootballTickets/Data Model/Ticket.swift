//
//  Ticket.swift
//  FootballTickets
//
//  Created by Sameer Dandekar on 3/31/20.
//  Copyright © 2020 Sameer Dandekar. All rights reserved.
//

import SwiftUI

struct Ticket: Hashable, Codable, Identifiable {
   
    var id: UUID        // Storage Type: String, Use Type (format): UUID
    var name: String
    var opponent: String
    var eventType: String
    var date: String
}
