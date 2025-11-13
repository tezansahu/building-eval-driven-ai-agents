"""
Mock Backend API for Campus Event Management System
This provides RESTful APIs for event registration, venue booking, and notifications
Designed to run on Google Colab with ngrok for public URL access
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date
import uvicorn
from threading import Thread
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Campus Event Management API",
    description="Mock backend for AI agent workshop",
    version="1.0.0"
)

# ============================================================================
# DATA MODELS
# ============================================================================

class Event(BaseModel):
    event_id: str
    name: str
    date: str
    time: str
    venue: str
    description: str
    max_participants: int
    participants: List[str] = []

class Venue(BaseModel):
    venue_id: str
    name: str
    capacity: int
    facilities: List[str]
    bookings: List[dict] = []

class RegistrationRequest(BaseModel):
    student_id: str
    student_name: str

class BookingRequest(BaseModel):
    club_name: str
    date: str
    time_slot: str
    purpose: str
    expected_attendees: int

class NotificationRequest(BaseModel):
    event_id: str
    message: str
    recipient_type: str  # "all_participants", "specific_students", "all_students"
    recipient_ids: Optional[List[str]] = None

# ============================================================================
# IN-MEMORY DATABASE
# ============================================================================

events_db = {
    "techfest2024": Event(
        event_id="techfest2024",
        name="TechFest 2024",
        date="2024-03-15",
        time="10:00-17:00",
        venue="Main Auditorium",
        description="Annual technical festival featuring coding competitions, robotics, and tech talks",
        max_participants=500,
        participants=[]
    ),
    "hackathon_spring": Event(
        event_id="hackathon_spring",
        name="Spring Hackathon 2024",
        date="2024-04-20",
        time="09:00-21:00",
        venue="Computer Lab 1",
        description="24-hour coding hackathon with prizes",
        max_participants=100,
        participants=[]
    ),
    "ai_workshop": Event(
        event_id="ai_workshop",
        name="AI & Machine Learning Workshop",
        date="2024-03-25",
        time="14:00-17:00",
        venue="Seminar Hall B",
        description="Hands-on workshop on building AI applications",
        max_participants=50,
        participants=[]
    ),
    "robotics_demo": Event(
        event_id="robotics_demo",
        name="Robotics Club Demo Day",
        date="2024-04-05",
        time="15:00-18:00",
        venue="Engineering Workshop",
        description="Showcase of student robotics projects",
        max_participants=200,
        participants=[]
    )
}

venues_db = {
    "aud_main": Venue(
        venue_id="aud_main",
        name="Main Auditorium",
        capacity=500,
        facilities=["Projector", "Sound System", "AC", "Stage"],
        bookings=[]
    ),
    "lab_cs1": Venue(
        venue_id="lab_cs1",
        name="Computer Lab 1",
        capacity=60,
        facilities=["Computers", "Projector", "Whiteboard", "AC"],
        bookings=[]
    ),
    "lab_cs2": Venue(
        venue_id="lab_cs2",
        name="Computer Lab 2",
        capacity=60,
        facilities=["Computers", "Projector", "Whiteboard"],
        bookings=[]
    ),
    "seminar_a": Venue(
        venue_id="seminar_a",
        name="Seminar Hall A",
        capacity=100,
        facilities=["Projector", "Sound System", "AC"],
        bookings=[]
    ),
    "seminar_b": Venue(
        venue_id="seminar_b",
        name="Seminar Hall B",
        capacity=80,
        facilities=["Projector", "Whiteboard", "AC"],
        bookings=[]
    ),
    "workshop": Venue(
        venue_id="workshop",
        name="Engineering Workshop",
        capacity=150,
        facilities=["Workbenches", "Tools", "Display Boards"],
        bookings=[]
    )
}

notifications_log = []

# ============================================================================
# EVENTS ENDPOINTS
# ============================================================================

@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Campus Event Management API is running",
        "endpoints": {
            "events": "/events",
            "venues": "/venues",
            "notifications": "/notifications",
            "docs": "/docs"
        }
    }

@app.get("/events", response_model=List[Event])
def list_events():
    """Get list of all events"""
    logger.info("Fetching all events")
    return list(events_db.values())

@app.get("/events/{event_id}", response_model=Event)
def get_event(event_id: str):
    """Get details of a specific event"""
    if event_id not in events_db:
        raise HTTPException(status_code=404, detail=f"Event '{event_id}' not found")
    logger.info(f"Fetching event: {event_id}")
    return events_db[event_id]

@app.post("/events/{event_id}/register")
def register_for_event(event_id: str, registration: RegistrationRequest):
    """Register a student for an event"""
    if event_id not in events_db:
        raise HTTPException(status_code=404, detail=f"Event '{event_id}' not found")
    
    event = events_db[event_id]
    
    # Check if already registered
    if registration.student_id in event.participants:
        return {
            "success": False,
            "message": f"Student {registration.student_name} is already registered for {event.name}"
        }
    
    # Check capacity
    if len(event.participants) >= event.max_participants:
        return {
            "success": False,
            "message": f"Event {event.name} is full (max capacity: {event.max_participants})"
        }
    
    # Register student
    event.participants.append(registration.student_id)
    logger.info(f"Registered student {registration.student_id} for event {event_id}")
    
    return {
        "success": True,
        "message": f"Successfully registered {registration.student_name} for {event.name}",
        "event_details": {
            "event_name": event.name,
            "date": event.date,
            "time": event.time,
            "venue": event.venue,
            "participants_count": len(event.participants)
        }
    }

@app.delete("/events/{event_id}/register/{student_id}")
def unregister_from_event(event_id: str, student_id: str):
    """Unregister a student from an event"""
    if event_id not in events_db:
        raise HTTPException(status_code=404, detail=f"Event '{event_id}' not found")
    
    event = events_db[event_id]
    
    if student_id not in event.participants:
        return {
            "success": False,
            "message": f"Student {student_id} is not registered for {event.name}"
        }
    
    event.participants.remove(student_id)
    logger.info(f"Unregistered student {student_id} from event {event_id}")
    
    return {
        "success": True,
        "message": f"Successfully unregistered from {event.name}"
    }

@app.get("/events/{event_id}/participants")
def get_event_participants(event_id: str):
    """Get list of participants for an event"""
    if event_id not in events_db:
        raise HTTPException(status_code=404, detail=f"Event '{event_id}' not found")
    
    event = events_db[event_id]
    logger.info(f"Fetching participants for event: {event_id}")
    
    return {
        "event_id": event_id,
        "event_name": event.name,
        "participant_count": len(event.participants),
        "participants": event.participants
    }

# ============================================================================
# VENUES ENDPOINTS
# ============================================================================

@app.get("/venues", response_model=List[Venue])
def list_venues():
    """Get list of all venues"""
    logger.info("Fetching all venues")
    return list(venues_db.values())

@app.get("/venues/{venue_id}", response_model=Venue)
def get_venue(venue_id: str):
    """Get details of a specific venue"""
    if venue_id not in venues_db:
        raise HTTPException(status_code=404, detail=f"Venue '{venue_id}' not found")
    logger.info(f"Fetching venue: {venue_id}")
    return venues_db[venue_id]

@app.get("/venues/{venue_id}/availability")
def check_venue_availability(venue_id: str, date: str, time_slot: Optional[str] = None):
    """Check if a venue is available on a specific date/time"""
    if venue_id not in venues_db:
        raise HTTPException(status_code=404, detail=f"Venue '{venue_id}' not found")
    
    venue = venues_db[venue_id]
    
    # Check bookings for the date
    bookings_on_date = [b for b in venue.bookings if b["date"] == date]
    
    if time_slot:
        # Check specific time slot
        conflicting_bookings = [b for b in bookings_on_date if b["time_slot"] == time_slot]
        available = len(conflicting_bookings) == 0
        
        return {
            "venue_id": venue_id,
            "venue_name": venue.name,
            "date": date,
            "time_slot": time_slot,
            "available": available,
            "existing_bookings": conflicting_bookings
        }
    else:
        # Return all bookings for the date
        return {
            "venue_id": venue_id,
            "venue_name": venue.name,
            "date": date,
            "available_slots": 8,  # Assume 8 time slots per day
            "booked_slots": len(bookings_on_date),
            "bookings": bookings_on_date
        }

@app.post("/venues/{venue_id}/book")
def book_venue(venue_id: str, booking: BookingRequest):
    """Book a venue for a specific date and time"""
    if venue_id not in venues_db:
        raise HTTPException(status_code=404, detail=f"Venue '{venue_id}' not found")
    
    venue = venues_db[venue_id]
    
    # Check capacity
    if booking.expected_attendees > venue.capacity:
        return {
            "success": False,
            "message": f"Venue capacity ({venue.capacity}) is less than expected attendees ({booking.expected_attendees})"
        }
    
    # Check availability
    conflicting_bookings = [
        b for b in venue.bookings 
        if b["date"] == booking.date and b["time_slot"] == booking.time_slot
    ]
    
    if conflicting_bookings:
        return {
            "success": False,
            "message": f"Venue {venue.name} is already booked for {booking.date} at {booking.time_slot}",
            "existing_booking": conflicting_bookings[0]
        }
    
    # Create booking
    new_booking = {
        "club_name": booking.club_name,
        "date": booking.date,
        "time_slot": booking.time_slot,
        "purpose": booking.purpose,
        "expected_attendees": booking.expected_attendees,
        "booked_at": datetime.now().isoformat()
    }
    
    venue.bookings.append(new_booking)
    logger.info(f"Booked venue {venue_id} for {booking.club_name} on {booking.date}")
    
    return {
        "success": True,
        "message": f"Successfully booked {venue.name} for {booking.club_name}",
        "booking_details": {
            "venue_name": venue.name,
            "venue_id": venue_id,
            "date": booking.date,
            "time_slot": booking.time_slot,
            "purpose": booking.purpose,
            "facilities": venue.facilities
        }
    }

# ============================================================================
# NOTIFICATIONS ENDPOINTS
# ============================================================================

@app.post("/notifications/send")
def send_notification(notification: NotificationRequest):
    """Send notification to event participants or students"""
    
    # Determine recipients
    recipients = []
    
    if notification.recipient_type == "all_participants":
        if notification.event_id not in events_db:
            raise HTTPException(status_code=404, detail=f"Event '{notification.event_id}' not found")
        event = events_db[notification.event_id]
        recipients = event.participants
    elif notification.recipient_type == "specific_students":
        if not notification.recipient_ids:
            raise HTTPException(status_code=400, detail="recipient_ids required for specific_students")
        recipients = notification.recipient_ids
    elif notification.recipient_type == "all_students":
        # In a real system, this would query all students
        recipients = ["all_students_broadcast"]
    else:
        raise HTTPException(status_code=400, detail="Invalid recipient_type")
    
    if not recipients:
        return {
            "success": False,
            "message": "No recipients found for this notification"
        }
    
    # Log notification
    notification_record = {
        "timestamp": datetime.now().isoformat(),
        "event_id": notification.event_id,
        "message": notification.message,
        "recipient_type": notification.recipient_type,
        "recipient_count": len(recipients),
        "recipients": recipients
    }
    
    notifications_log.append(notification_record)
    logger.info(f"Sent notification to {len(recipients)} recipients for event {notification.event_id}")
    
    return {
        "success": True,
        "message": f"Notification sent to {len(recipients)} recipients",
        "details": {
            "event_id": notification.event_id,
            "recipient_count": len(recipients),
            "sent_at": notification_record["timestamp"]
        }
    }

@app.get("/notifications/log")
def get_notifications_log():
    """Get history of all sent notifications"""
    logger.info(f"Fetching notifications log ({len(notifications_log)} notifications)")
    return {
        "total_notifications": len(notifications_log),
        "notifications": notifications_log
    }

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def run_server(port: int = 8000):
    """Run the FastAPI server"""
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

def run_in_thread(port: int = 8000):
    """Run server in background thread (useful for Colab)"""
    thread = Thread(target=run_server, args=(port,), daemon=True)
    thread.start()
    logger.info(f"Server started in background on port {port}")
    return thread

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import sys
    
    port = 8000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    
    print(f"""
    ╔══════════════════════════════════════════════════════════╗
    ║   Campus Event Management API - Mock Backend           ║
    ╠══════════════════════════════════════════════════════════╣
    ║   Server running on: http://localhost:{port}            ║
    ║   API Documentation: http://localhost:{port}/docs       ║
    ║   Health Check: http://localhost:{port}/                ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    run_server(port)
