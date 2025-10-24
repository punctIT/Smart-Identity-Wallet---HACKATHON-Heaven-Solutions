from __future__ import annotations

from pathlib import Path
from typing import Optional, Dict, Any
import threading
import base64

from kivy.logger import Logger
from kivy.metrics import dp, sp
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.card import MDCard


class SaveScreen(Screen):
    """Screen that processes OCR for scanned documents and allows editing of extracted data."""

    def __init__(self, server=None, **kwargs):
        super().__init__(name='save_data', **kwargs)
        self.server = server
        self.image_path: Optional[str] = None
        self.image_base64: Optional[str] = None
        self.ocr_data: Optional[Dict[str, Any]] = None
        self.processing = False
        
        # UI elements
        self.progress_bar: Optional[MDProgressBar] = None
        self.status_label: Optional[MDLabel] = None
        self.fields_container: Optional[MDBoxLayout] = None
        self.save_button: Optional[MDRaisedButton] = None
        self.back_button: Optional[MDIconButton] = None
        self.text_fields: Dict[str, MDTextField] = {}
        
        self._build_ui()

    def set_image_path(self, path: str) -> None:
        """Set the path of the image to process and convert to base64."""
        self.image_path = path
        Logger.info(f"SaveScreen: Converting image to base64: {path}")
        
        try:
            # Convert image to base64
            with open(path, 'rb') as image_file:
                image_data = image_file.read()
                self.image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            Logger.info(f"SaveScreen: Image converted to base64 (length: {len(self.image_base64)})")
            
            # Delete the original file after converting to base64
            self._delete_image_file()
            
        except Exception as e:
            Logger.error(f"SaveScreen: Failed to convert image to base64: {e}")
            self.image_base64 = None

    def _build_ui(self) -> None:
        """Build the UI layout."""
        self.main_box = BoxLayout(orientation='vertical', size_hint_y=1, spacing=dp(16), padding=[dp(24), dp(24), dp(24), 0])

        # Header with back button and title
        header = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(56),
            spacing=dp(12),
        )
        
        self.back_button = MDIconButton(
            icon="arrow-left",
            theme_icon_color="Primary",
            on_release=self._go_back,
        )
        header.add_widget(self.back_button)
        
        self.title_lbl = Label(
            text="[color=#2696FF][b]PROCESARE DOCUMENT[/b][/color]",
            markup=True,
            font_size=sp(28),
            color=(0.25, 0.60, 1.00, 1),
            halign="left",
            valign="middle"
        )
        self.title_lbl.bind(size=lambda instance, value: setattr(instance, "text_size", value))
        header.add_widget(self.title_lbl)
        self.main_box.add_widget(header)

        # Subtitle
        self.subtitle_lbl = Label(
            text="Verificați și editați datele extrase din document.",
            font_size=sp(16),
            color=(0.7, 0.76, 0.86, 1),
            size_hint_y=None,
            height=dp(28),
            halign="left",
            valign="middle"
        )
        self.subtitle_lbl.bind(size=lambda instance, value: setattr(instance, "text_size", value))
        self.main_box.add_widget(self.subtitle_lbl)
        
        self.main_box.add_widget(Label(size_hint_y=None, height=dp(28)))

        # Processing section
        self.processing_card = MDCard(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(12),
            size_hint_y=None,
            height=dp(120),
            elevation=2,
        )
        
        self.status_label = MDLabel(
            text="Pregătire pentru procesare...",
            theme_text_color="Primary",
            halign="center",
            font_style="Body1",
        )
        self.processing_card.add_widget(self.status_label)
        
        self.progress_bar = MDProgressBar(
            size_hint_y=None,
            height=dp(4),
        )
        self.processing_card.add_widget(self.progress_bar)
        self.main_box.add_widget(self.processing_card)

        # Fields container for OCR results
        self.fields_container = MDBoxLayout(
            orientation="vertical",
            spacing=dp(12),
            size_hint_y=None,
        )
        self.fields_container.bind(minimum_height=self.fields_container.setter('height'))
        
        # Wrap fields in scroll view
        fields_scroll = ScrollView()
        fields_scroll.add_widget(self.fields_container)
        self.main_box.add_widget(fields_scroll)

        # Save button
        self.save_button = MDRaisedButton(
            text="Salvează Date",
            size_hint_y=None,
            height=dp(40),
            disabled=True,
            opacity=0,
            on_release=self._save_data,
        )
        self.main_box.add_widget(self.save_button)
        
        self.add_widget(self.main_box)

    def on_pre_enter(self, *args):
        """Called when screen is about to be entered."""
        if self.image_base64 and not self.processing:
            Logger.info("SaveScreen: Starting OCR processing")
            self._start_ocr_processing()
        return super().on_pre_enter(*args)

    def _start_ocr_processing(self) -> None:
        """Start OCR processing in background thread."""
        if self.processing:
            return
            
        self.processing = True
        self.progress_bar.start()
        self.status_label.text = "Procesez documentul..."
        
        # Hide fields and save button during processing
        self.fields_container.clear_widgets()
        self.text_fields.clear()
        self.save_button.disabled = True
        self.save_button.opacity = 0
        
        # Start processing in background thread
        thread = threading.Thread(target=self._process_ocr)
        thread.daemon = True
        thread.start()

    def _process_ocr(self) -> None:
        """Process OCR in background thread."""
        try:
            if not self.server or not hasattr(self.server, 'sent_OCR_image'):
                raise Exception("Server connection not available")
            
            if not self.image_base64:
                raise Exception("No image data available")
                
            Logger.info(f"SaveScreen: Sending base64 image for OCR (length: {len(self.image_base64)})")
            
            # Send base64 string to server for OCR processing
            ocr_result = self.server.sent_OCR_image(self.image_base64)
            
            if ocr_result:
                Logger.info("SaveScreen: OCR processing successful")
                # Schedule UI update on main thread
                Clock.schedule_once(lambda dt: self._on_ocr_success(ocr_result), 0)
            else:
                Logger.error("SaveScreen: OCR processing failed")
                Clock.schedule_once(lambda dt: self._on_ocr_error("OCR processing failed"), 0)
                
        except Exception as e:
            error_msg = str(e)
            Logger.error(f"SaveScreen: OCR error: {error_msg}")
            Clock.schedule_once(lambda dt: self._on_ocr_error(error_msg), 0)

    def _on_ocr_success(self, result: Dict[str, Any]) -> None:
        """Handle successful OCR result on main thread."""
        self.processing = False
        self.progress_bar.stop()
        self.status_label.text = "Procesare completă! Verificați și editați datele:"
        
        self.ocr_data = result
        self._build_editable_fields(result)
        self.save_button.disabled = False
        self.save_button.opacity = 1

    def _on_ocr_error(self, error_msg: str) -> None:
        """Handle OCR error on main thread."""
        self.processing = False
        self.progress_bar.stop()
        self.status_label.text = f"Eroare la procesare: {error_msg}"
        
        # Add retry button
        retry_btn = MDRaisedButton(
            text="Încearcă din nou",
            size_hint_y=None,
            height=dp(40),
            on_release=lambda *_: self._start_ocr_processing(),
        )
        self.fields_container.add_widget(retry_btn)

    def _build_editable_fields(self, data: Dict[str, Any]) -> None:
        """Build editable text fields from OCR data."""
        self.fields_container.clear_widgets()
        self.text_fields.clear()
        
        # Extract relevant data from OCR response
        ocr_content = data.get('content', {})
        
        if isinstance(ocr_content, dict):
            # If content is structured data, create fields for each key
            for key, value in ocr_content.items():
                if isinstance(value, (str, int, float)):
                    field_name = key.replace('_', ' ').title()
                    field = MDTextField(
                        hint_text=field_name,
                        text=str(value),
                        size_hint_y=None,
                        height=dp(56),
                    )
                    self.text_fields[key] = field
                    self.fields_container.add_widget(field)
        elif isinstance(ocr_content, str):
            # If content is a string, create a simple text area
            field = MDTextField(
                hint_text="Text Extras",
                text=ocr_content,
                multiline=True,
                size_hint_y=None,
                height=dp(120),
            )
            self.text_fields['extracted_text'] = field
            self.fields_container.add_widget(field)
        else:
            # Fallback: create a general text field
            field = MDTextField(
                hint_text="Date Extrase",
                text=str(data),
                multiline=True,
                size_hint_y=None,
                height=dp(120),
            )
            self.text_fields['raw_data'] = field
            self.fields_container.add_widget(field)

    def _save_data(self, *args) -> None:
        """Save the edited data."""
        if not self.text_fields:
            return
            
        # Collect data from all fields
        edited_data = {}
        for key, field in self.text_fields.items():
            edited_data[key] = field.text.strip()
        
        Logger.info(f"SaveScreen: Saving edited data: {edited_data}")
        print(f"💾 Date salvate: {edited_data}")
        
        # TODO: Here you can add code to save the data to database, 
        # send to server, or store locally as needed
        
        # Show success and go back
        self.status_label.text = "Date salvate cu succes!"
        Clock.schedule_once(lambda dt: self._go_back(), 1.5)

    def _delete_image_file(self) -> None:
        """Delete the original image file."""
        if not self.image_path:
            return
            
        try:
            image_path = Path(self.image_path)
            if image_path.exists():
                image_path.unlink()
                Logger.info(f"SaveScreen: Deleted original image: {self.image_path}")
        except Exception as e:
            Logger.warning(f"SaveScreen: Failed to delete image: {e}")

    def _go_back(self, *args) -> None:
        """Navigate back to previous screen."""
        # Reset state
        self.image_path = None
        self.image_base64 = None
        self.ocr_data = None
        self.processing = False
        self.fields_container.clear_widgets()
        self.text_fields.clear()
        
        manager = getattr(self, "manager", None)
        if not manager:
            return
            
        if manager.has_screen("home"):
            manager.current = "home"
        else:
            manager.current = manager.previous()