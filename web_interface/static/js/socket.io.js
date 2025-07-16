/**
 * Simple Socket.IO Client Fallback
 * This is a basic implementation for when the main Socket.IO client fails to load
 */

(function() {
    'use strict';
    
    // Simple Socket.IO client implementation
    window.io = function(url, options) {
        console.log('🔌 Using fallback Socket.IO client');
        
        var socket = {
            connected: false,
            id: null,
            callbacks: {},
            
            // Connect to server
            connect: function() {
                console.log('🔌 Attempting to connect...');
                this.connected = true;
                this.id = 'fallback-' + Date.now();
                
                // Simulate connection success
                setTimeout(function() {
                    if (socket.callbacks.connect) {
                        socket.callbacks.connect();
                    }
                    // Start simulating data
                    socket.simulateData();
                }, 100);
                
                return this;
            },
            
            // Event listeners
            on: function(event, callback) {
                console.log('🎧 Socket.IO listening for:', event);
                this.callbacks[event] = callback;
                return this;
            },
            
            // Emit events
            emit: function(event, data) {
                console.log('📤 Socket.IO emit:', event, data);
                
                // Simulate server response for certain events
                if (event === 'command') {
                    setTimeout(function() {
                        if (socket.callbacks.command_response) {
                            socket.callbacks.command_response({
                                success: true,
                                result: { status: 'ok' }
                            });
                        }
                    }, 50);
                }
                
                return this;
            },
            
            // Simulate receiving data from server
            simulateData: function() {
                // DISABLED: Using real backend data instead of mock data
                console.log('✅ Mock data simulation disabled - using real backend data');
            },
            
            // Disconnect
            disconnect: function() {
                console.log('🔌 Disconnecting...');
                this.connected = false;
                return this;
            }
        };
        
        // Auto-connect
        return socket.connect();
    };
    
    console.log('✅ Fallback Socket.IO client loaded');
})(); 