//
//  ScanQRBarcode.swift
//  BarcodeScanner
//
//  Created by Sameer Dandekar on 2/15/20.
//  Copyright © 2020 Sameer Dandekar. All rights reserved.
//
 
import SwiftUI
import AVFoundation
 
struct ScanQRBarcode: View {
 
    @State var barcode: String = ""
    @State var lightOn: Bool = false
   
    var body: some View {
        VStack {
            // Show barcode scanning camera view if no barcode is present
            if barcode.isEmpty {
                /*
                 Display barcode scanning camera view on the background layer because
                 we will display the results on the foreground layer in the same view.
                 */
                ZStack {
                    /*
                     BarcodeScanner displays the barcode scanning camera view, obtains the barcode
                     value, and stores it into the @State variable 'barcode'. When the @State value
                     changes,the view invalidates its appearance and recomputes this body view.
                    
                     When this body view is recomputed, 'barcode' will not be empty and the
                     else part of the if statement will be executed, which displays barcode
                     processing results on the foreground layer in this same view.
                     */
                    BarcodeScanner(code: self.$barcode)
                   
                    // Display the flashlight button created in FlashlightButton.swift
                    flashlightButtonView
                   
                    /*
                     Display the scan focus region image to guide the user during scanning.
                     The image is constructed in ScanFocusRegion.swift upon app launch.
                     */
                    scanFocusRegionImage
                }
            } else {
                // Show QR barcode processing results
                qrBarcodeProcessingResults
            }
        }   // End of VStack
        .onDisappear() {
            self.lightOn = false
        }
    }
   
    var flashlightButtonView: some View {
        return VStack {
            HStack {
                Spacer()    // Spaces to show the button on the right of the screen
                FlashlightButton(lightOn: self.$lightOn)
                    .padding()
            }
            Spacer()        // Spaces to show the button on the top of the screen
        }
        // Using Spacer(), the button is positioned on the top right corner of the screen
    }
   
    var qrBarcodeProcessingResults: some View {
       
        if barcode.hasPrefix("http") {
            return AnyView(WebView(url: self.barcode))
        }
        return AnyView(Text("Scanned QR Barcode Value: \(self.barcode)"))
    }
}
 
struct ScanQRBarcode_Previews: PreviewProvider {
    static var previews: some View {
        ScanQRBarcode()
    }
}
 
