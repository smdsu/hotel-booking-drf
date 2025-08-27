# Hotel Booking API

A Django REST Framework service for managing hotel rooms and bookings with PostgreSQL database.

## Features

- **Room Management**: Add, delete, and list hotel rooms with pricing
- **Booking System**: Create and manage room reservations with date validation
- **Conflict Detection**: Automatic validation to prevent double-booking
- **RESTful API**: JSON-based HTTP endpoints
- **Docker Support**: Easy deployment with docker-compose

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.10+ (for local development)

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd hotel-booking-drf
```

2. Create `.env` file:
```bash
# Database
DB_NAME=hotel_booking
DB_USER=admin
DB_PASSWORD=your_password
DB_HOST=postgres
DB_PORT=5432

# Django
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

3. Start the services:
```bash
docker-compose up -d
```

4. Access the API:
- API Base URL: `http://localhost:8000/api/v1/`
- Swagger UI: `http://localhost:8000/api/v1/schema/swagger-ui/`
- API Schema: `http://localhost:8000/api/v1/schema/`

### Local Development

1. Install dependencies:
```bash
pip install poetry
poetry install
```

2. Set up environment variables and run migrations:
```bash
python manage.py migrate
python manage.py runserver
```

## API Endpoints

### Room Management

#### Create Room
**POST** `/api/v1/rooms/rooms/`

Creates a new hotel room.

**Request Body:**
```json
{
    "description": "Deluxe Suite with Ocean View",
    "price": "299.99"
}
```

**Response:**
```json
{
    "room_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/v1/rooms/rooms/ \
  -H "Content-Type: application/json" \
  -d '{"description": "Deluxe Suite", "price": "299.99"}'
```

#### List Rooms
**GET** `/api/v1/rooms/rooms/`

Returns a list of all hotel rooms with optional sorting.

**Query Parameters:**
- `ordering`: Sort by `price`, `-price`, `created_at`, `-created_at`

**Response:**
```json
[
    {
        "room_id": "550e8400-e29b-41d4-a716-446655440000",
        "description": "Deluxe Suite with Ocean View",
        "price": "299.99",
        "active": true,
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
    }
]
```

**cURL Examples:**
```bash
# Get all rooms
curl http://localhost:8000/api/v1/rooms/rooms/

# Sort by price (ascending)
curl "http://localhost:8000/api/v1/rooms/rooms/?ordering=price"

# Sort by price (descending)
curl "http://localhost:8000/api/v1/rooms/rooms/?ordering=-price"

# Sort by creation date (newest first)
curl "http://localhost:8000/api/v1/rooms/rooms/?ordering=-created_at"
```

#### Get Room Details
**GET** `/api/v1/rooms/rooms/{room_id}/`

Returns detailed information about a specific room including its bookings.

**Response:**
```json
{
    "room_id": "550e8400-e29b-41d4-a716-446655440000",
    "price": "299.99",
    "bookings": [
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "check_in": "2024-02-01T14:00:00Z",
            "check_out": "2024-02-03T11:00:00Z"
        }
    ]
}
```

#### Delete Room
**DELETE** `/api/v1/rooms/rooms/{room_id}/`

Deletes a room and all its associated bookings.

**cURL Example:**
```bash
curl -X DELETE http://localhost:8000/api/v1/rooms/rooms/550e8400-e29b-41d4-a716-446655440000/
```

### Booking Management

#### Create Booking
**POST** `/api/v1/booking/booking/`

Creates a new room reservation with automatic conflict detection.

**Request Body:**
```json
{
    "room": "550e8400-e29b-41d4-a716-446655440000",
    "check_in": "2024-02-01T14:00:00Z",
    "check_out": "2024-02-03T11:00:00Z"
}
```

**Response:**
```json
{
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "room": "550e8400-e29b-41d4-a716-446655440000",
    "check_in": "2024-02-01T14:00:00Z",
    "check_out": "2024-02-03T11:00:00Z"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/v1/booking/booking/ \
  -H "Content-Type: application/json" \
  -d '{
    "room": "550e8400-e29b-41d4-a716-446655440000",
    "check_in": "2024-02-01T14:00:00Z",
    "check_out": "2024-02-03T11:00:00Z"
  }'
```

#### List Bookings for a Room
**GET** `/api/v1/booking/booking/?room={room_id}`

Returns all bookings for a specific room, sorted by check-in date.

**Response:**
```json
[
    {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "room": "550e8400-e29b-41d4-a716-446655440000",
        "check_in": "2024-02-01T14:00:00Z",
        "check_out": "2024-02-03T11:00:00Z"
    },
    {
        "id": "456e7890-e89b-12d3-a456-426614174000",
        "room": "550e8400-e29b-41d4-a716-446655440000",
        "check_in": "2024-02-05T14:00:00Z",
        "check_out": "2024-02-07T11:00:00Z"
    }
]
```

**cURL Example:**
```bash
curl "http://localhost:8000/api/v1/booking/booking/?room=550e8400-e29b-41d4-a716-446655440000"
```

#### Delete Booking
**DELETE** `/api/v1/booking/booking/{booking_id}/`

Deletes a specific booking.

**cURL Example:**
```bash
curl -X DELETE http://localhost:8000/api/v1/booking/booking/123e4567-e89b-12d3-a456-426614174000/
```

## Data Models

### Room
- `room_id`: UUID (Primary Key)
- `description`: Text description of the room
- `price`: Decimal field with minimum value 0.01
- `active`: Boolean status
- `created_at`: Timestamp of creation
- `updated_at`: Timestamp of last update

### Booking
- `id`: UUID (Primary Key)
- `room`: Foreign key to Room model
- `check_in`: DateTime of check-in
- `check_out`: DateTime of check-out
- `created_at`: Timestamp of creation
- `updated_at`: Timestamp of last update

## Business Logic

### Booking Validation
- **Date Validation**: Check-out date must be after check-in date
- **Conflict Detection**: Prevents double-booking by checking for overlapping date ranges
- **Room Existence**: Validates that the room exists before creating a booking

### Room Management
- **Soft Delete**: Rooms are marked as inactive rather than physically deleted
- **Cascade Delete**: Deleting a room removes all associated bookings
- **Price Validation**: Ensures price is always positive

## Database Schema

The application uses PostgreSQL with the following key features:
- UUID primary keys for better distribution and security
- Proper indexing on foreign keys and date fields
- Timestamp tracking for audit purposes
- Decimal fields for precise price calculations

## Performance Considerations

- **Database Indexing**: Foreign keys and date fields are indexed for optimal query performance
- **Query Optimization**: Uses Django ORM efficiently with select_related for room details
- **Pagination**: Large result sets can be paginated (implemented via DRF pagination)

## Testing

Run the test suite:
```bash
python manage.py test
```

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `/api/v1/schema/swagger-ui/`
- OpenAPI Schema: `/api/v1/schema/`

## Deployment

### Production Considerations
- Set `DEBUG=False` in production
- Use environment variables for sensitive configuration
- Configure proper database connection pooling
- Set up reverse proxy (nginx) for production
- Use gunicorn or uwsgi instead of Django development server

### Environment Variables
```bash
# Required
SECRET_KEY=your_secret_key
DB_NAME=hotel_booking
DB_USER=admin
DB_PASSWORD=secure_password
DB_HOST=postgres
DB_PORT=5432

# Optional
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

## Architecture Decisions

### Framework Choice
- **Django REST Framework**: Provides robust API building capabilities, automatic serialization, and comprehensive validation
- **PostgreSQL**: Reliable, ACID-compliant database with excellent JSON support and performance

### API Design
- **RESTful**: Follows REST principles for intuitive API design
- **JSON**: Standard format for data exchange
- **UUIDs**: Better than sequential IDs for distributed systems

### Data Validation
- **Model-level**: Core business rules enforced at the model level
- **Serializer-level**: Input validation and transformation
- **Database-level**: Constraints and relationships

## License

This project is licensed under the MIT License - see the LICENSE file for details.
