from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from .models import Playerdetail,Turf,Booking,Review,Payment,TurfSlot, BlockedSlot, TurfHoliday,Notification
from django.contrib.auth import authenticate, login as auth_login,logout
from django.db.models import Q,Sum,Avg
from datetime import datetime, timedelta
from django.utils import timezone
from datetime import date
from django.core.paginator import Paginator


def landing(request):
    return render(request,'landing.html')

def register(request):
     if request.method=='POST':
            username=request.POST.get('username')
            email=request.POST.get('email')
            phone=request.POST.get('phone')
            password=request.POST.get('password')
            confirmPassword=request.POST.get('confirmPassword')
        
                    
            if Playerdetail.objects.filter(username=username):
               messages.error(request,"Username already exist")
               return render(request,'register.html')

            if password != confirmPassword:
              messages.error(request, "Passwords do not match")
              return render(request, 'register.html')
            
            Playerdetail.objects.create(username=username,email=email,phone=phone,password=password,confirmPassword=confirmPassword)
            messages.success(request,"Registration Successfull")
            return redirect('login')
        
     return render(request,'register.html')

def login(request):

  

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = Playerdetail.objects.get(username=username)

        except Playerdetail.DoesNotExist:

            messages.error(request, "Invalid Username or Password.")
            return render(request, 'login.html')

        if user is not None and user.password == password:

            # Store logged-in player ID in session
            request.session['player_id'] = user.id

            messages.success(
                request,
                f"Welcome back {username}!"
            )

            return redirect('home', user.id)

        else:

            messages.error(
                request,
                'Invalid username or password'
            )

            return render(request, 'login.html')

    return render(request, 'login.html')

def home(request,id):
    user=Playerdetail.objects.get(id=id)
    query = request.GET.get('q', '')
    location = request.GET.get('location', '')
    turf_type = request.GET.get('turf_type', '')
    price_per_hour = request.GET.get('price_per_hour', '')
    availability = request.GET.get('availability', '')

    # Start with all turfs
    turfs = Turf.objects.all()

    # Search by turf name or location
    if query:
        turfs = turfs.filter(
            Q(turf_name__icontains=query) |
            Q(location__icontains=query)
        )

    # Location filter
    if location:
        turfs = turfs.filter(location__icontains=location)

    # Turf type filter
    if turf_type:
        turfs = turfs.filter(turf_type__iexact=turf_type)

    # Price filter
    if price_per_hour == 'low':
        turfs = turfs.filter(price_per_hour__lt=500)

    elif price_per_hour == 'medium':
        turfs = turfs.filter(
            price_per_hour__gte=500,
            price_per_hour__lte=1000
        )

    elif price_per_hour == 'high':
        turfs = turfs.filter(price_per_hour__gt=1000)

    # Availability/status filter
    if availability:
        turfs = turfs.filter(status=availability)

    return render(request, 'home.html', {
        'user': user,
        'turfs': turfs,
        'query': query,
        'location': location,
        'turf_type': turf_type,
        'price_per_hour': price_per_hour,
        'availability': availability
    })

def userprofile(request,id):
     user=Playerdetail.objects.get(id=id)
     return render(request,'userprofile.html',{'user':user})

def editprofile(request,id):
     user = Playerdetail.objects.get(id=id)

     if request.method == 'POST':
            user.username = request.POST.get('username')
            user.email = request.POST.get('email')
            user.phone = request.POST.get('phone')
     
            user.save()
     
            return redirect('userprofile',user.id)
     return render(request,'editprofile.html',{'user':user})

def logout_user(request):
    request.session.pop('player_id', None)

    logout(request)

    return redirect('login')

def admin_login(request):
    if request.method=='POST':
         username=request.POST.get('username')
         password=request.POST.get('password')
         user=authenticate(request,username=username,password=password)

         if user is not None and user.is_superuser:
            auth_login(request,user)
            messages.success(request,'Admin login successfull')
            return redirect('admin_dashboard')
         else:
           messages.error(request,'Invalid username or password')
        
    return render(request,'admin_login.html')

def admin_availability(request):

    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()

    turfs = Turf.objects.all().order_by('turf_name')

    if query:
        turfs = turfs.filter(
            Q(turf_name__icontains=query) |
            Q(location__icontains=query)
        )

    if status_filter == 'active':
        turfs = turfs.filter(is_active=True)
    elif status_filter == 'inactive':
        turfs = turfs.filter(is_active=False)

    today = timezone.localdate()

    # Attach per-turf stats
    turf_data = []
    for turf in turfs:
        slot_count = TurfSlot.objects.filter(turf=turf).count()
        bookings_today = Booking.objects.filter(turf=turf, booking_date=today).count()
        holiday_active = TurfHoliday.objects.filter(
            turf=turf,
            start_date__lte=today,
            end_date__gte=today
        ).first()
        turf_data.append({
            'turf': turf,
            'slot_count': slot_count,
            'bookings_today': bookings_today,
            'holiday': holiday_active,
        })

    total_turfs = Turf.objects.count()
    active_turfs = Turf.objects.filter(is_active=True).count()
    inactive_turfs = Turf.objects.filter(is_active=False).count()
    total_bookings_today = Booking.objects.filter(booking_date=today).count()

    context = {
        'turf_data': turf_data,
        'query': query,
        'status_filter': status_filter,
        'total_turfs': total_turfs,
        'active_turfs': active_turfs,
        'inactive_turfs': inactive_turfs,
        'total_bookings_today': total_bookings_today,
        'today': today,
    }

    return render(request, 'admin_availability.html', context)


def admin_dashboard(request):

    # Total users
    total_users = Playerdetail.objects.count()

    # Total turfs
    total_turfs = Turf.objects.count()

    # Total bookings
    total_bookings = Booking.objects.count()

    # Today's bookings
    today = timezone.localdate()

    todays_bookings = Booking.objects.filter(
        booking_date=today
    ).count()

    # Confirmed bookings
    confirmed_bookings = Booking.objects.filter(
        status='confirmed'
    ).count()

    # Cancelled bookings
    cancelled_bookings = Booking.objects.filter(
        status='cancelled'
    ).count()

    # Pending payments
    pending_payments = Payment.objects.filter(
        status='pending'
    ).count()

    # Total revenue from paid payments
    total_revenue = Payment.objects.filter(
        status='paid'
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0

    context = {
        'total_users': total_users,
        'total_turfs': total_turfs,
        'total_bookings': total_bookings,
        'todays_bookings': todays_bookings,
        'confirmed_bookings': confirmed_bookings,
        'cancelled_bookings': cancelled_bookings,
        'pending_payments': pending_payments,
        'total_revenue': total_revenue,
    }

    return render(
        request,
        'admin_dashboard.html',
        context
    )


def manageusers(request):
    query = request.GET.get('q')
    
    if query:
            users = Playerdetail.objects.filter(
                Q(username__icontains=query) |
                Q(email__icontains=query)     
            )
    else:
            users = Playerdetail.objects.all()
    
    return render(request, 'manageusers.html', {
            'users': users,
            'query': query
        })
    
def block_user(request, id):
    user = Playerdetail.objects.get(id=id)
    user.is_block = True
    user.save()

    return redirect('manageusers')

def unblock_user(request, id):
    user = Playerdetail.objects.get(id=id)
    user.is_block = False
    user.save()

    return redirect('manageusers')

def viewuser(request, id):
     user = Playerdetail.objects.get(id=id)

     return render(request, 'viewuser.html', {
        'user': user
    })

def edituser(request, id):
     user = Playerdetail.objects.get(id=id)

     if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.phone = request.POST.get('phone')

        user.save()

        return redirect('manageusers')
     return render(request, 'edituser.html', {'user': user})


def deleteuser(request, id):
     user = Playerdetail.objects.get(id=id)

     user.delete()
     return redirect('manageusers')

def notifications(request):

    return render(request, 'notifications.html')



def manageturfs(request):

    if request.method == 'POST':

        Turf.objects.create(
            turf_name=request.POST.get('turf_name'),
            location=request.POST.get('location'),
            turf_type=request.POST.get('turf_type'),
            image=request.FILES.get('image'),
            description=request.POST.get('description'),
            price_per_hour=request.POST.get('price_per_hour'),
            available_facilities=request.POST.get('available_facilities'),
            address=request.POST.get('address'),
            opening_time=request.POST.get('opening_time'),
            closing_time=request.POST.get('closing_time')
        )

        return redirect('manageturfs')

    query = request.GET.get('q', '')

    if query:
            turfs = Turf.objects.filter(
               Q(turf_name__icontains=query) |
               Q(location__icontains=query) |
               Q(turf_type__icontains=query)
        )
    else:
          turfs = Turf.objects.all()

    

    return render(request, 'manageturfs.html', {
        'turfs': turfs,
        'query': query
    })


def editturf(request, id):
    turf = Turf.objects.get(id=id)

    if request.method == 'POST':
        turf.turf_name = request.POST.get('turf_name')
        turf.turf_type = request.POST.get('turf_type')
        turf.location = request.POST.get('location')
        turf.price_per_hour = request.POST.get('price_per_hour')
        turf.address = request.POST.get('address')
        turf.description = request.POST.get('description')
        turf.opening_time = request.POST.get('opening_time')
        turf.closing_time = request.POST.get('closing_time')
        turf.available_facilities = request.POST.get('available_facilities')

        status = request.POST.get("status")

        if status == "active":
            turf.is_active = True
        else:
            turf.is_active = False

        
        if request.FILES.get("image"):
            turf.image = request.FILES.get("image")

        turf.save()

        return redirect('manageturfs')

    return render(request, 'editturf.html', {
        'turf': turf
    })

def viewturf(request, id):
    turf = Turf.objects.get(id=id)

    return render(request, 'viewturf.html', {
        'turf': turf
    })

def delete_turf(request, id):

    turf = Turf.objects.get(id=id)

    turf.delete()

    return redirect("manageturfs")


def turfdetails(request, id):

   

    turf = get_object_or_404(Turf, id=id)

    player_id = request.session.get('player_id')

    if not player_id:
        return redirect('login')

    user = get_object_or_404(
        Playerdetail,
        id=player_id
    )

    return render(request, 'turfdetails.html', {
        'turf': turf,
        'user': user
    })


def booknow(request, user_id, turf_id):

    user = get_object_or_404(Playerdetail, id=user_id)
    turf = get_object_or_404(Turf, id=turf_id)

    selected_date = request.GET.get('date')

    if not selected_date:
        selected_date = datetime.today().date()
    else:
        selected_date = datetime.strptime(
            selected_date,
            '%Y-%m-%d'
        ).date()

    # Check if selected date falls within a holiday/maintenance period
    holiday_obj = TurfHoliday.objects.filter(
        turf=turf,
        start_date__lte=selected_date,
        end_date__gte=selected_date,
    ).first()
    is_holiday_date = holiday_obj is not None

    # Get existing bookings
    bookings = Booking.objects.filter(
        turf=turf,
        booking_date=selected_date
    )

    booked_slots = []

    for booking in bookings:
        booked_slots.append(booking.start_time)

    # Get blocked slots for the selected date
    blocked_slots = BlockedSlot.objects.filter(
        turf=turf,
        date=selected_date
    )

    # Generate time slots
    slots = []

    if not is_holiday_date:
        current_time = datetime.combine(
            selected_date,
            turf.opening_time
        )

        closing_datetime = datetime.combine(
            selected_date,
            turf.closing_time
        )

        while current_time < closing_datetime:

            slot_start = current_time.time()

            next_time = current_time + timedelta(hours=1)

            if next_time > closing_datetime:
                break

            slot_end = next_time.time()

            # Check if this slot overlaps any blocked slot
            is_blocked = any(
                slot_start < b.to_time and slot_end > b.from_time
                for b in blocked_slots
            )

            slots.append({
                'start': slot_start,
                'end': slot_end,
                'booked': slot_start in booked_slots,
                'blocked': is_blocked,
            })

            current_time = next_time

    # When user clicks Continue / Book
    if request.method == 'POST':

        booking_date = request.POST.get('booking_date')
        start_time = request.POST.get('start_time')

        if not booking_date or not start_time:

            messages.error(
                request,
                'Please select a date and time slot.'
            )

            return redirect(
                'book_now',
                user_id=user.id,
                turf_id=turf.id
            )

        # Convert booking_date string to a proper date object
        try:
            booking_date_obj = datetime.strptime(booking_date, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Invalid date format.')
            return redirect(f'/booknow/{user.id}/{turf.id}/')

        # Check whether slot is already booked
        already_booked = Booking.objects.filter(
            turf=turf,
            booking_date=booking_date_obj,
            start_time=start_time
        ).exists()

        if already_booked:

            messages.error(
                request,
                'Sorry, this time slot has already been booked.'
            )

            return redirect(
                f'/booknow/{user.id}/{turf.id}/?date={booking_date}'
            )

        # Parse start/end times for this slot
        try:
            parsed_start = datetime.strptime(start_time, "%H:%M:%S").time()
        except ValueError:
            parsed_start = datetime.strptime(start_time, "%H:%M").time()
        parsed_end = (datetime.combine(datetime.today(), parsed_start) + timedelta(hours=1)).time()

        # Check whether slot overlaps a blocked slot (use date object, not string)
        is_blocked = BlockedSlot.objects.filter(
            turf=turf,
            date=booking_date_obj,
            from_time__lt=parsed_end,
            to_time__gt=parsed_start,
        ).exists()

        if is_blocked:
            messages.error(
                request,
                'Sorry, this time slot is blocked and cannot be booked.'
            )
            return redirect(
                f'/booknow/{user.id}/{turf.id}/?date={booking_date}'
            )

        # Check whether the date falls within a TurfHoliday
        is_holiday = TurfHoliday.objects.filter(
            turf=turf,
            start_date__lte=booking_date_obj,
            end_date__gte=booking_date_obj,
        ).exists()

        if is_holiday:
            messages.error(
                request,
                'Sorry, the turf is closed on this date (holiday/maintenance).'
            )
            return redirect(
                f'/booknow/{user.id}/{turf.id}/?date={booking_date}'
            )

        # Store booking information temporarily in session
        request.session['booking_turf_id'] = turf.id
        request.session['booking_user_id'] = user.id
        request.session['booking_date'] = booking_date
        request.session['booking_start_time'] = start_time

        # Go to confirmation page
        return redirect('confirmbooking')

    return render(
        request,
        'booknow.html',
        {
            'user': user,
            'turf': turf,
            'slots': slots,
            'blocked_slots': blocked_slots,
            'is_holiday_date': is_holiday_date,
            'holiday_obj': holiday_obj,
            'selected_date': selected_date,
            'today': datetime.today().date(),
        }
    )

def confirmbooking(request):

    turf_id = request.session.get("booking_turf_id")
    user_id = request.session.get("booking_user_id")
    booking_date = request.session.get("booking_date")
    start_time = request.session.get("booking_start_time")

    # If booking information is missing
    if not turf_id or not user_id or not booking_date or not start_time:

        player_id = request.session.get('player_id')

        if player_id:
            return redirect('home', id=player_id)

        return redirect('login')

    # Get turf and user
    turf = get_object_or_404(Turf, id=turf_id)
    user = get_object_or_404(Playerdetail, id=user_id)

    # Convert start time
    start = datetime.strptime(start_time, "%H:%M:%S")
    end = start + timedelta(hours=1)

    # Convert date
    date_object = datetime.strptime(booking_date, "%Y-%m-%d")

    # Display values
    booking_date_display = date_object.strftime("%B %d, %Y")
    start_display = start.strftime("%I:%M %p")
    end_display = end.strftime("%I:%M %p")

    # When user confirms booking
    if request.method == "POST":

        # Convert booking_date string → date object for reliable ORM filtering
        try:
            booking_date_obj = datetime.strptime(booking_date, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Invalid booking date.')
            player_id = request.session.get('player_id')
            return redirect('home', id=player_id) if player_id else redirect('login')

        already_booked = Booking.objects.filter(
            turf=turf,
            booking_date=booking_date_obj,
            start_time=start_time
        ).exists()

        if already_booked:

            messages.error(
                request,
                "Sorry, this time slot has already been booked."
            )

            return redirect(
                "booknow",
                user_id=user.id,
                turf_id=turf.id
            )

        # Check whether slot overlaps a blocked slot (race-condition guard)
        try:
            cb_start = datetime.strptime(start_time, "%H:%M:%S").time()
        except ValueError:
            cb_start = datetime.strptime(start_time, "%H:%M").time()
        cb_end = (datetime.combine(datetime.today(), cb_start) + timedelta(hours=1)).time()

        is_blocked = BlockedSlot.objects.filter(
            turf=turf,
            date=booking_date_obj,
            from_time__lt=cb_end,
            to_time__gt=cb_start,
        ).exists()

        if is_blocked:
            messages.error(
                request,
                "Sorry, this time slot is blocked and cannot be booked."
            )
            return redirect(
                "booknow",
                user_id=user.id,
                turf_id=turf.id
            )

        # Check whether the date falls within a TurfHoliday (race-condition guard)
        is_holiday = TurfHoliday.objects.filter(
            turf=turf,
            start_date__lte=booking_date_obj,
            end_date__gte=booking_date_obj,
        ).exists()

        if is_holiday:
            messages.error(
                request,
                "Sorry, the turf is closed on this date (holiday/maintenance)."
            )
            return redirect(
                "booknow",
                user_id=user.id,
                turf_id=turf.id
            )

        # Create booking
        booking = Booking.objects.create(
            turf=turf,
            player=user,
            booking_date=booking_date,
            start_time=start_time,
            end_time=end.time(),
            price=turf.price_per_hour,
            status='confirmed',
        )


        Notification.objects.create(
            player=user,
            booking=booking,
            notification_type='confirmation',
            message=f"Your booking at {turf.turf_name} has been confirmed."
        )

        # Create payment
        Payment.objects.create(
            booking=booking,
            amount=turf.price_per_hour,
            status='pending'
        )

        # Clear temporary booking session
        request.session.pop("booking_turf_id", None)
        request.session.pop("booking_user_id", None)
        request.session.pop("booking_date", None)
        request.session.pop("booking_start_time", None)

        messages.success(
            request,
            "Booking created successfully. Please complete your payment."
        )

        return redirect('payment', booking_id=booking.id)

    # Display confirmation page for GET request
    return render(request, "confirmbooking.html", {
        "turf": turf,
        "user": user,
        "booking_date": booking_date_display,
        "start_time": start_display,
        "end_time": end_display,
        "price": turf.price_per_hour,
    })

    

def admin_booking_details(request, booking_id):

    booking = get_object_or_404(
        Booking.objects.select_related(
            'player',
            'turf'
        ),
        id=booking_id
    )

    return render(
        request,
        'admin_booking_details.html',
        {
            'booking': booking
        }
    )

def mybookings(request, id):

    user = get_object_or_404(Playerdetail, id=id)

    bookings = Booking.objects.filter(
        player=user
    ).select_related('turf').order_by('-booking_date', '-start_time')

    today = date.today()

    upcoming = bookings.filter(
        booking_date__gte=today,
        status='confirmed'
    )

    completed = bookings.filter(
        booking_date__lt=today,
        status='confirmed'
    )

    cancelled = bookings.filter(
        status='cancelled'
    )

    return render(request, 'mybookings.html', {
        'user': user,
        'upcoming': upcoming,
        'completed': completed,
        'cancelled': cancelled,

        'upcoming_count': upcoming.count(),
        'completed_count': completed.count(),
        'cancelled_count': cancelled.count(),
    })  

def cancel_booking(request, booking_id):

    if request.method == 'POST':

        booking = get_object_or_404(
            Booking,
            id=booking_id
        )

        # Change booking status
        booking.status = 'cancelled'
        booking.save()

        # Create cancellation notification
        Notification.objects.create(
            player=booking.player,
            booking=booking,
            notification_type='cancellation',
            message=f"Your booking at {booking.turf.turf_name} has been cancelled."
        )

    return redirect(
        'booking_details',
        booking_id=booking_id
    )

    

def booking_history(request,id):

    user = get_object_or_404(Playerdetail, id=id)

   

    bookings = Booking.objects.filter(
        player=user
    ).exclude(
        status='Upcoming'
    )

    # Search
    search = request.GET.get('search', '')

    if search:
        bookings = bookings.filter(
            turf__turf_name__icontains=search
        )

    # Status filter
    status = request.GET.get('status', '')

    if status:
        bookings = bookings.filter(
            status=status
        )

    # Sorting
    sort = request.GET.get('sort', 'newest')

    if sort == 'oldest':
        bookings = bookings.order_by('booking_date')
    else:
        bookings = bookings.order_by('-booking_date')

    return render(
        request,
        'booking_history.html',
        {
            'user': user,
            'bookings': bookings,
            'search': search,
            'status': status,
            'sort': sort
        }
    )


def reviews_ratings(request):

    player_id = request.session.get('player_id')

    if not player_id:
        return redirect('login')

    # Get logged-in player
    user = get_object_or_404(Playerdetail, id=player_id)

    # Get all bookings of this player
    bookings = Booking.objects.filter(
        player=user
    ).select_related('turf').order_by(
        '-booking_date',
        '-start_time'
    )

    # Check whether each booking already has a review
    for booking in bookings:
        booking.review_obj = Review.objects.filter(
            booking=booking
        ).first()

    # Submit review
    if request.method == 'POST':

        booking_id = request.POST.get('booking_id')
        rating = request.POST.get('rating')
        review_text = request.POST.get('review', '').strip()

        booking = get_object_or_404(
            Booking,
            id=booking_id,
            player=user
        )

        # Check if already reviewed
        if Review.objects.filter(booking=booking).exists():

            messages.warning(
                request,
                'You have already reviewed this booking.'
            )

            return redirect('reviews_ratings')

        # Check rating and review
        if not rating or not review_text:

            messages.error(
                request,
                'Please provide a rating and review.'
            )

            return redirect('reviews_ratings')

        # Create review
        Review.objects.create(
            booking=booking,
            player=user,
            turf=booking.turf,
            rating=int(rating),
            review=review_text
        )

        messages.success(
            request,
            'Your review has been submitted successfully!'
        )

        return redirect('reviews_ratings')

    return render(
        request,
        'reviews_ratings.html',
        {
            'bookings': bookings,
            'user': user,
            'today': date.today()
        }
    )

def admin_reviews_ratings(request):

    # Get all reviews
    reviews = Review.objects.select_related(
        'player',
        'turf'
    ).all().order_by('-created_at')

    # Search
    search_query = request.GET.get('q', '').strip()

    if search_query:
        reviews = reviews.filter(
            Q(player__username__icontains=search_query) |
            Q(turf__turf_name__icontains=search_query) |
            Q(review__icontains=search_query)
        )

    # Rating filter
    selected_rating = request.GET.get('rating', '').strip()

    if selected_rating:
        reviews = reviews.filter(
            rating=int(selected_rating)
        )

    # Statistics
    total_reviews = Review.objects.count()

    average_rating = Review.objects.aggregate(
        average=Avg('rating')
    )['average'] or 0

    five_star_reviews = Review.objects.filter(
        rating=5
    ).count()

    # You don't currently have a flagged field
    flagged_reviews = 0

    # Pagination
    paginator = Paginator(reviews, 4)

    page_number = request.GET.get('page')

    reviews = paginator.get_page(page_number)

    context = {
        'reviews': reviews,

        'total_reviews': total_reviews,
        'average_rating': average_rating,
        'five_star_reviews': five_star_reviews,
        'flagged_reviews': flagged_reviews,

        'search_query': search_query,
        'selected_rating': selected_rating,
    }

    return render(
        request,
        'admin_reviews_ratings.html',
        context
    )



def admin_delete_review(request, review_id):

    if request.method == 'POST':

        review = get_object_or_404(
            Review,
            id=review_id
        )

        review.delete()

        messages.success(
            request,
            'Review removed successfully.'
        )

    return redirect('admin_reviews_ratings')

def payment(request, booking_id):

    booking = get_object_or_404(
        Booking,
        id=booking_id
    )

    payment = get_object_or_404(
        Payment,
        booking=booking
    )

    if request.method == 'POST':

        payment.status = 'paid'
        payment.save()

        messages.success(
            request,
            'Payment successful!'
        )

        return redirect(
            'payment_success',
            booking_id=booking.id
        )

    return render(
        request,
        'payment.html',
        {
            'booking': booking,
            'payment': payment
        }
    )

def payment_success(request, booking_id):

    booking = get_object_or_404(
        Booking,
        id=booking_id
    )

    payment = get_object_or_404(
        Payment,
        booking=booking
    )

    return render(
        request,
        'payment_success.html',
        {
            'booking': booking,
            'payment': payment,
            'user': booking.player
        }
    )

def activate_turf(request, turf_id):
    turf = get_object_or_404(Turf, id=turf_id)
    turf.is_active = True
    turf.save()

    return redirect('manageturfs')


def deactivate_turf(request, turf_id):
    turf = get_object_or_404(Turf, id=turf_id)
    turf.is_active = False
    turf.save()

    return redirect('manageturfs')

from datetime import date

def turf_availability(request, turf_id):

    turf = get_object_or_404(Turf, id=turf_id)

    today = date.today()

    # Selected date
    selected_date = request.GET.get('date')

    if not selected_date:
        selected_date = today.isoformat()


    # All time slots for this turf
    slots = TurfSlot.objects.filter(
        turf=turf
    ).order_by('start_time')


    # Blocked slots for the selected date (used in the slot availability grid)
    blocked_slots = BlockedSlot.objects.filter(
        turf=turf,
        date=selected_date
    ).order_by('from_time')

    # All upcoming blocked slots (today and future) for the flash card
    all_blocked_slots = BlockedSlot.objects.filter(
        turf=turf,
        date__gte=today
    ).order_by('date', 'from_time')


    # Upcoming holidays only (end_date >= today)
    holidays = TurfHoliday.objects.filter(
        turf=turf,
        end_date__gte=today
    ).order_by('start_date')


    # Bookings for selected date
    bookings = Booking.objects.filter(
        turf=turf,
        booking_date=selected_date
    )


    # Determine status of every time slot
    slot_data = []

    for slot in slots:

        status = 'available'


        # Check blocked slots
        for blocked in blocked_slots:

            if (
                slot.start_time < blocked.to_time
                and
                slot.end_time > blocked.from_time
            ):

                status = 'blocked'
                break


        # Check bookings
        if status == 'available':

            for booking in bookings:

                if (
                    slot.start_time < booking.end_time
                    and
                    slot.end_time > booking.start_time
                ):

                    status = 'booked'
                    break


        slot_data.append({
            'slot': slot,
            'status': status
        })


    context = {
        'turf': turf,
        'slots': slots,
        'slot_data': slot_data,
        'blocked_slots': blocked_slots,
        'all_blocked_slots': all_blocked_slots,
        'holidays': holidays,
        'bookings': bookings,
        'selected_date': selected_date,
        'today': today,
    }


    return render(
        request,
        'turf_availability.html',
        context
    )

    

    

def add_slot(request, turf_id):

    turf = get_object_or_404(Turf, id=turf_id)

    if request.method == 'POST':

        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        TurfSlot.objects.create(
            turf=turf,
            start_time=start_time,
            end_time=end_time
        )

        return redirect('turf_availability', turf_id=turf.id)

    return render(
        request,
        'add_slot.html',
        {'turf': turf}
    ) 


def block_slot(request, turf_id):

    turf = get_object_or_404(Turf, id=turf_id)

    if request.method == 'POST':

        date = request.POST.get('date')
        from_time = request.POST.get('from_time')
        to_time = request.POST.get('to_time')
        reason = request.POST.get('reason')

        BlockedSlot.objects.create(
            turf=turf,
            date=date,
            from_time=from_time,
            to_time=to_time,
            reason=reason
        )

        return redirect('turf_availability', turf_id=turf.id)



def update_turf_hours(request, turf_id):

    turf = get_object_or_404(Turf, id=turf_id)

    if request.method == 'POST':

        opening_time = request.POST.get('opening_time')
        closing_time = request.POST.get('closing_time')
        is_active = request.POST.get('is_active')

        turf.opening_time = opening_time
        turf.closing_time = closing_time

        if is_active == 'active':
            turf.is_active = True
        else:
            turf.is_active = False

        turf.save()

        return redirect('turf_availability', turf_id=turf.id)

    return redirect('turf_availability', turf_id=turf.id)



def set_holiday(request, turf_id):

    turf = get_object_or_404(Turf, id=turf_id)

    if request.method == 'POST':

        status = request.POST.get('status')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        reason = request.POST.get('reason')

        TurfHoliday.objects.create(
            turf=turf,
            status=status,
            start_date=start_date,
            end_date=end_date,
            reason=reason
        )

    return redirect(
        'turf_availability',
        turf_id=turf.id
    )




def managebookings(request):

    # Get all bookings
    bookings = Booking.objects.select_related(
        'player',
        'turf'
    ).all().order_by('-created_at')

    # Search
    search_query = request.GET.get('q', '').strip()

    # Filters
    selected_date = request.GET.get('date', '').strip()
    selected_turf = request.GET.get('turf', '').strip()
    selected_status = request.GET.get('status', '').strip()

    # Search by Booking ID, Player username or Turf name
    if search_query:

        search_filter = (
            Q(player__username__icontains=search_query) |
            Q(turf__turf_name__icontains=search_query)
        )

        # If search is a number, also search booking ID
        if search_query.isdigit():
            search_filter |= Q(id=int(search_query))

        bookings = bookings.filter(search_filter)

    # Filter by date
    if selected_date:
        bookings = bookings.filter(
            booking_date=selected_date
        )

    # Filter by turf
    if selected_turf:
        bookings = bookings.filter(
            turf_id=selected_turf
        )

    # Filter by status
    if selected_status:
        bookings = bookings.filter(
            status=selected_status
        )

    # Total number of filtered bookings
    total_bookings = bookings.count()

    # Pagination
    paginator = Paginator(bookings, 10)
    page_number = request.GET.get('page')
    bookings = paginator.get_page(page_number)

    # All turfs for dropdown
    turfs = Turf.objects.all().order_by('turf_name')

    context = {
        'bookings': bookings,
        'turfs': turfs,

        'search_query': search_query,
        'selected_date': selected_date,
        'selected_turf': selected_turf,
        'selected_status': selected_status,

        'total_bookings': total_bookings,
    }

    return render(
        request,
        'managebookings.html',
        context
    )

    

def update_booking_status(request, booking_id, status):

    booking = get_object_or_404(
        Booking,
        id=booking_id
    )

    if status == 'confirmed':

        booking.status = 'confirmed'
        booking.save()

        Notification.objects.create(
            player=booking.player,
            booking=booking,
            notification_type='confirmation',
            message=f"Your booking at {booking.turf.turf_name} has been confirmed."
        )

    elif status == 'cancelled':

        booking.status = 'cancelled'
        booking.save()

        Notification.objects.create(
            player=booking.player,
            booking=booking,
            notification_type='cancellation',
            message=f"Your booking at {booking.turf.turf_name} has been cancelled."
        )

    return redirect('managebookings')

   

def admin_booking_detail(request, booking_id):

    booking = get_object_or_404(
        Booking,
        id=booking_id
    )

    return render(
        request,
        'admin_booking_detail.html',
        {
            'booking': booking
        }
    )


def managepayments(request):

    # Get all payments
    payments = Payment.objects.select_related(
        'booking__player',
        'booking__turf'
    ).all().order_by('-payment_date')

    # Search
    search_query = request.GET.get('q', '').strip()

    # Filters
    selected_status = request.GET.get('status', '').strip()
    selected_sort = request.GET.get('sort', 'newest').strip()

    # Search by booking ID, username or turf name
    if search_query:

        search_filter = (
            Q(booking__player__username__icontains=search_query) |
            Q(booking__turf__turf_name__icontains=search_query)
        )

        # Search by booking ID
        if search_query.isdigit():
            search_filter |= Q(booking__id=int(search_query))

        payments = payments.filter(search_filter)

    # Status filter
    if selected_status:
        payments = payments.filter(
            status=selected_status
        )

    # Sorting
    if selected_sort == 'oldest':
        payments = payments.order_by('payment_date')

    elif selected_sort == 'high':
        payments = payments.order_by('-amount')

    elif selected_sort == 'low':
        payments = payments.order_by('amount')

    else:
        # Newest
        payments = payments.order_by('-payment_date')

    # Statistics
    total_revenue = Payment.objects.filter(
        status='paid'
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0

    paid_count = Payment.objects.filter(
        status='paid'
    ).count()

    pending_count = Payment.objects.filter(
        status='pending'
    ).count()

    failed_count = Payment.objects.filter(
        status='failed'
    ).count()

    refunded_count = Payment.objects.filter(
        status='refunded'
    ).count()

    # Total filtered payments
    total_payments = payments.count()

    # Pagination
    paginator = Paginator(payments, 4)

    page_number = request.GET.get('page')

    payments = paginator.get_page(page_number)

    context = {
        'payments': payments,
        'search_query': search_query,

        'selected_status': selected_status,
        'selected_sort': selected_sort,

        'total_revenue': total_revenue,
        'paid_count': paid_count,
        'pending_count': pending_count,
        'failed_count': failed_count,
        'refunded_count': refunded_count,

        'total_payments': total_payments,
    }

    return render(
        request,
        'managepayments.html',
        context
    )


def admin_payment_detail(request, payment_id):

    payment = get_object_or_404(
        Payment.objects.select_related(
            'booking__player',
            'booking__turf'
        ),
        id=payment_id
    )

    return render(
        request,
        'admin_payment_detail.html',
        {
            'payment': payment
        }
    )

def notifications(request):

    player_id = request.session.get('player_id')

    if not player_id:
        return redirect('login')

    user = get_object_or_404(
        Playerdetail,
        id=player_id
    )

    selected_filter = request.GET.get('filter', 'all')

    notifications = Notification.objects.filter(
        player=user
    )

    # Filter notifications
    if selected_filter == 'unread':

        notifications = notifications.filter(
            is_read=False
        )

    elif selected_filter in [
        'confirmation',
        'cancellation',
        'reminder',
        'status_change'
    ]:

        notifications = notifications.filter(
            notification_type=selected_filter
        )

    notifications = notifications.order_by('-created_at')

    # Count unread notifications
    unread_count = Notification.objects.filter(
        player=user,
        is_read=False
    ).count()

    return render(
        request,
        'notifications.html',
        {
            'notifications': notifications,
            'user': user,
            'unread_count': unread_count,
            'selected_filter': selected_filter,
        }
    )

    
def mark_all_notifications_read(request):

    player_id = request.session.get('player_id')

    if not player_id:
        return redirect('login')

    if request.method == 'POST':

        Notification.objects.filter(
            player_id=player_id,
            is_read=False
        ).update(is_read=True)

    return redirect('notifications')



def clear_all_notifications(request):

    player_id = request.session.get('player_id')

    if not player_id:
        return redirect('login')

    if request.method == 'POST':

        Notification.objects.filter(
            player_id=player_id
        ).delete()

    return redirect('notifications')