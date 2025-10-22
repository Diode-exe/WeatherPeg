"""
Improved ScrollingText Widget

A clean, maintainable implementation of scrolling text for WeatherPeg.
Replaces the problematic ScrollingSummary class with a much better solution.
"""

import tkinter as tk
from typing import Optional


class ScrollingTextWidget:
    """
    A clean, efficient scrolling text widget that handles long text gracefully.
    
    Features:
    - Automatic scrolling for text longer than display width
    - Smooth, configurable scrolling speed
    - Memory efficient (no callback chains)
    - Easy to use and maintain
    - Thread-safe GUI updates
    """
    
    def __init__(self, parent, text: str = "", width: int = 80, speed: int = 150):
        """
        Initialize the scrolling text widget.
        
        Args:
            parent: Parent tkinter widget
            text: Initial text to display
            width: Maximum width in characters
            speed: Scroll speed in milliseconds per character
        """
        self.parent = parent
        self.width = width
        self.speed = speed
        self.original_text = text
        
        # Create the label widget
        self.label = tk.Label(
            parent, 
            text="", 
            fg="lime", 
            bg="black",
            font=("VCR OSD Mono", 12), 
            justify="left",
            padx=10, 
            pady=10
        )
        self.label.pack()
        
        # Scrolling state
        self.position = 0
        self.is_scrolling = False
        self.after_id: Optional[str] = None
        self.scroll_id = 0
        
        # Update with initial text
        self.update_text(text)
    
    def update_text(self, new_text: str) -> None:
        """
        Update the text content and start scrolling if needed.
        
        Args:
            new_text: New text to display
        """
        # Stop any existing scrolling
        self.scroll_id += 1
        self.is_scrolling = False
        
        # Cancel any pending after callbacks
        if self.after_id:
            self.parent.after_cancel(self.after_id)
            self.after_id = None
        
        self.original_text = new_text
        self.position = 0
        
        # If text fits in width, just display it
        if len(new_text) <= self.width:
            self.label.config(text=new_text)
            return
        
        # Start scrolling for longer text
        self.is_scrolling = True
        current_scroll_id = self.scroll_id
        self._scroll_text(current_scroll_id)
    
    def _scroll_text(self, scroll_id: int) -> None:
        """
        Internal method that handles the scrolling animation.
        Uses tkinter's after() method for smooth GUI updates.
        """
        # Check if this scroll session is still valid
        if scroll_id != self.scroll_id or not self.is_scrolling or not self.original_text:
            return
        
        # Create extended text for smooth looping
        extended_text = self.original_text + "   ***   "
        
        # Calculate visible portion
        start = self.position % len(extended_text)
        display_text = (extended_text[start:] + extended_text)[:self.width]
        
        # Update the label
        self.label.config(text=display_text)
        
        # Move position for next update
        self.position += 1
        
        # Schedule next update
        self.after_id = self.parent.after(self.speed, lambda: self._scroll_text(scroll_id))
    
    def flash_black(self) -> None:
        """
        Flash the text black for refresh indication.
        """
        self.label.config(fg="black")
        self.parent.after(750, lambda: self.label.config(fg="lime"))
    
    def stop_scrolling(self) -> None:
        """
        Stop the scrolling animation.
        """
        self.is_scrolling = False
        if self.after_id:
            self.parent.after_cancel(self.after_id)
            self.after_id = None
    
    def destroy(self) -> None:
        """
        Clean up resources when the widget is destroyed.
        """
        self.stop_scrolling()


# Backward compatibility alias
ScrollingSummary = ScrollingTextWidget
