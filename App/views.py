# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.http import JsonResponse
from datetime import datetime
from django import forms
from .decorators import admin_only
import uuid
import pyrebase
import requests
import uuid
import json
from django.urls import reverse

config = {
    "apiKey": "AIzaSyD_2f-l_8SdOrR4oCRtcyceGY9xyz8FdnE",
    "authDomain": "palace-d2b7f.firebaseapp.com",
    "databaseURL": "https://palace-d2b7f-default-rtdb.firebaseio.com",
    "projectId": "palace-d2b7f",
    "storageBucket": "palace-d2b7f.appspot.com",
    "messagingSenderId": "225914163841",
    "appId": "1:225914163841:web:58ca77402cf3166078f380",
    "measurementId": "G-ZRMK9KFP6C"
}

# config = {
#     "apiKey": "AIzaSyDfOPsPiKZJtTvowMkgkBC52mLHFv0agCk",
#     "authDomain": "tabib-a4529.firebaseapp.com",
#     "databaseURL": "https://tabib-a4529-default-rtdb.europe-west1.firebasedatabase.app",
#     "projectId": "tabib-a4529",
#     "storageBucket": "tabib-a4529.appspot.com",
#     "messagingSenderId": "484081647935",
#     "appId": "1:484081647935:web:fcfb4c8f2dfb468cbcd38a",
#     "measurementId": "G-5WS88GHY67",
# }

# config = {
#     "apiKey": "AIzaSyDo4BUk0x-5ogFESIxQGpthJZfbZQQbLEM",
#     "authDomain": "data-test-27937.firebaseapp.com",
#     "databaseURL": "https://data-test-27937-default-rtdb.europe-west1.firebasedatabase.app/",
#     "projectId": "data-test-27937",
#     "storageBucket": "data-test-27937.appspot.com",
#     "messagingSenderId": "607758979508",
#     "appId": "1:607758979508:web:bc8c1787d8e50a48d7a2e1",
#     "measurementId": "G-RQ54N3ZCEL",
# }
firebase = pyrebase.initialize_app(config)
authe = firebase.auth()
database = firebase.database()


class LoginForm(forms.Form):
    username = forms.CharField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput)

def convert_date_to_timestamp(date_str):
    # Assuming the input date string is in the format 'DD/MM/YYYY'
    date_object = datetime.strptime(date_str, '%d/%m/%Y')

    iso_format_date = date_object.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    
    return iso_format_date


def user_login(request):
    if request.user.is_authenticated:
        return redirect("/")
    else:
        if request.method == "POST":
            # print(request)
            form = LoginForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data["username"]
                password = form.cleaned_data["password"]
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    auth_login(request, user)
                    # Redirect to a success page.
                    return redirect("/")  # Change 'dashboard' to the desired URL name.
                else:
                    # Return an 'invalid login' error message.
                    return render(
                        request,
                        "login/login.html",
                        {"form": form, "error_message": "Invalid login credentials."},
                    )
        else:
            form = LoginForm()
        return render(request, "login/login.html", {"form": form})


def user_dashboard(request):
    # return render(request, "index-3.html", {"form": []})
    start_date = datetime.today().strftime('01/%m/%Y')
    end_date = datetime.today().strftime('%d/%m/%Y')
    date_today = datetime.today().strftime('%d/%m/%Y')

    stack = database.child('Client').order_by_child("Fait").start_at(start_date).end_at(end_date).get()

    total_prix = 0
    total_prix_month = 0
    total_Rooms_Av = 0
    Rooms_Av = 0
    total_Rooms_N_Av = 35
    total_price_per_day = {}

    for entry in stack.each():
        entry_date = datetime.strptime(entry.val().get('Fait'), '%d/%m/%Y')
        if datetime.strptime(entry.val().get('Fait'), '%d/%m/%Y') >= datetime.strptime(start_date, '%d/%m/%Y') and datetime.strptime(entry.val().get('Fait'), '%d/%m/%Y') <= datetime.strptime(end_date, '%d/%m/%Y'):
            prix_value = entry.val().get('Prix')
            if prix_value and prix_value.strip() != '':
                total_prix_month += int(prix_value) 
                total_price_per_day.setdefault(entry_date.date(), 0)
                total_price_per_day[entry_date.date()] += int(prix_value)

    # for date, total_price in total_price_per_day.items():
    #     print(f"{date.strftime('%d/%m/%Y')}: {total_price}")

    data_new = []
    data_av = []
    data_in = []
    data_out = []
    stack = database.child('Client').order_by_child("Fait").equal_to(datetime.today().strftime('%d/%m/%Y')).get()  

    for entry in stack.each():
        # print(entry.val().get('Fait'))
        if  int(entry.val().get("Prix")) > 0:
            data_new.append({
                "nom":entry.val().get("Nom"),
                "prenom":entry.val().get("Prenom"),
                "Prix":entry.val().get('Prix'),
            })
        prix_value = entry.val().get('Prix')
        if prix_value and prix_value.strip() != '':
            if prix_value:
                total_prix += int(prix_value)
    

    Rooms = database.child('Client').order_by_child("Check_out").start_at(datetime.today().strftime('%d/%m/%Y')).get()
    
    for entry in Rooms.each():
        # print(entry.val().get('Check_out'))
        if datetime.strptime(entry.val().get('Check_out'), '%d/%m/%Y') > datetime.strptime(date_today, '%d/%m/%Y'):
            
            Rooms_Av = entry.val().get('N_chamber')
            Rooms_n = entry.val().get('Fait')
            Rooms_P = entry.val().get('Prenom') + ' '  + entry.val().get('Nom')

            if Rooms_Av and Rooms_Av.strip() != '':
                if Rooms_Av:
                    total_Rooms_Av += 1
                    data_av.append({
                        "nom_in":entry.val().get("Nom"),
                        "prenom_in":entry.val().get("Prenom"),
                        "Prix_in":entry.val().get('Prix'),
                        "date_out" : entry.val().get('Check_out'),
                        "date_in" : entry.val().get('Check_in'),
                        "room" : Rooms_Av,

                    })
                    # print(entry.val().get('Check_out'))
                    # print(entry.val().get('N_chamber'))
        elif datetime.strptime(entry.val().get('Check_out'), '%d/%m/%Y') == datetime.strptime(date_today, '%d/%m/%Y'):
            Rooms_Av = entry.val().get('N_chamber')
            if Rooms_Av and Rooms_Av.strip() != '':
                try:
                    stripped_rooms_av = Rooms_Av.lstrip('0')
                    stripped_rooms_av = ''.join(char if char.isdigit() or char == ' ' else '' for char in stripped_rooms_av)
                    result = eval(stripped_rooms_av)
                    if result <= 35:
                        data_out.append({
                        "nom":entry.val().get("Nom"),
                        "prenom":entry.val().get("Prenom"),
                        "Prix":entry.val().get('Prix'),
                        "date_in" : entry.val().get('Check_in'),
                        "date_out" : entry.val().get('Check_out'),
                        "room" : Rooms_Av,
                        })
                except ValueError as e:
                    # Handle the case where the expression cannot be evaluated as an integer
                        print(f"Error: {e}")
                        
        if datetime.strptime(entry.val().get('Check_in'), '%d/%m/%Y') == datetime.strptime(date_today, '%d/%m/%Y'):
            Rooms_Av = entry.val().get('N_chamber')
            if Rooms_Av and Rooms_Av.strip() != '':
                try:
                    stripped_rooms_av = Rooms_Av.lstrip('0')
                    stripped_rooms_av = ''.join(char if char.isdigit() or char == ' ' else '' for char in stripped_rooms_av)
                    result = eval(stripped_rooms_av)
                    if result <= 35:
                        data_in.append({
                        "nom":entry.val().get("Nom"),
                        "prenom":entry.val().get("Prenom"),
                        "Prix":entry.val().get('Prix'),
                        "date_in" : entry.val().get('Check_in'),
                        "date_out" : entry.val().get('Check_out'),
                        "room" : Rooms_Av,
                        })
                except ValueError as e:
                    # Handle the case where the expression cannot be evaluated as an integer
                        print(f"Error: {e}")

    if request.method == "POST":
        First_Name = request.POST['nom']
        Last_Name = request.POST['prenom']
        Check_in = request.POST['check_in']
        Check_out = request.POST['check_out']
        Room = request.POST['n_chamber']
        Prix = request.POST['prix']
        # Unpaid_Price = request.POST['Unpaid_Price']
        # Nationalite = request.POST['Nationalite']
        # Domicile = request.POST['Domicile']
        # Num_Cin_Pas = request.POST['Num_Cin_Pas']
        # Image_Cin_Pas = request.POST['Image_Cin_Pas']
        data = {
            "Prenom": First_Name,
            "Nom": Last_Name,
            "Check_in": Check_in,
            "Check_out": Check_out,
            "N_chamber": Room,
            "Prix": Prix,
            # "Prix_R": Unpaid_Price,
            # "Nationalite": Nationalite,
            # "Domicile": Domicile,
            # "Cin_Pas": Num_Cin_Pas,
            # "Image_Cin_Pas": Image_Cin_Pas,
            "Fait": datetime.today().strftime('%d/%m/%Y'),
            # "ID": Id_value,
            }
    # print(data_new)
    
    context = {
        'data_out': data_out,
        'data_av': data_av,
        'data_in': data_in,
        'data_new': data_new,
        'stack': stack.val(),
        'total_prix': total_prix,
        'total_prix_month': total_prix_month,
        'total_Rooms_Av': total_Rooms_Av,
        'total_Rooms_N_Av': total_Rooms_N_Av - total_Rooms_Av,
        'total_price_per_day': total_price_per_day,
        'date_today': datetime.today().strftime('%d/%m/%Y'),
    }
    # return JsonResponse({"data": data_new})
    return render(request, "dashboard.html", context)


def user_logout(request):
    logout(request)
    return redirect("/login")


def test(request):
    stack = database.child("Appointments").get().val()
    return render(request, "test.html", {"data": stack})


################################ Doctor  #################################
@admin_only
def doctor_list(request):
    # doctors = Doctor.objects.all()
    doctors = {}
    # print("TEST ")
    Doctors = database.child("Doctors").get().val()

    return render(request, "doctor/doctor-list.html", {"doctors": Doctors})

@admin_only
def doctor_detail(request, pk):
    if request.method == "POST":
        # Your existing logic for updating the doctor data
        # print(request.POST.get("ajax_request"))
        if request.POST.get("ajax_request"):
            # If it's an AJAX request, respond with a JSON indicating the redirect URL
            return JsonResponse({"redirect_url": reverse("doctor_detail", args=[pk])})

    else:
        # Handle the case where it's a GET request (non-AJAX)
        # Retrieve the doctor data and render the HTML page
        ref = database.child("Doctors")

        doctor_data = ref.child(pk).get()  # Replace with your logic to get doctor data
        return render(
            request, "doctor/doctor-profile.html", {"doctor_data": doctor_data.val()}
        )

@admin_only
def doctor_create(request):
    # if request.method == "POST":
    #     form = DoctorForm(request.POST)
    #     if form.is_valid():
    #         doctor = form.save()
    #         return redirect("doctor_detail", pk=doctor.pk)
    # else:
    #     form = DoctorForm()
    # return render(request, "doctor_form.html", {"form": form})
    doctor = {
        "first_name": request.POST.get("first_name", ""),
        "last_name": request.POST.get("last_name", ""),
        "email": request.POST.get("email", ""),
        "mobile_no": request.POST.get("mobile_no", ""),
        "gender": request.POST.get("gender", ""),
        "date_of_birth": request.POST.get("date_of_birth", ""),
        "languages": request.POST.get("languages", ""),
        "nationality": request.POST.get("nationality", ""),
        "city": request.POST.get("city", ""),
        "zip_code": request.POST.get("zip", ""),
        "user_role": request.POST.get("user_role", ""),
        "address": request.POST.get("address", ""),
        "bio": request.POST.get("bio", ""),
    }
    # Generate a unique identifier manually (rendem id)
    rendem_id = "Doctor_" + str(uuid.uuid4())

    # Update the data_Patients dictionary with the rendem id
    doctor["Doctor_id"] = rendem_id
    # Now you can push the data to Firebase using the unique identifier
    database.child("Doctors").child(rendem_id).set(doctor)
    return render(request, "doctor/add-doctor.html")

@admin_only
def doctor_edit(request, pk):
    # doctor = get_object_or_404(Doctor, pk=pk)

    print(
        "===============================================================================>",
        request.GET.get("ajax_request") == "1",
    )
    if request.GET.get("ajax_request") == "1":
        # If it's an AJAX GET request, return the doctor data in JSON
        return JsonResponse({"redirect_url": reverse("doctor_edit", args=[pk])})
    else:
        # If it's a regular GET request, render the HTML page
        ref = database.child("Doctors")
        doctor_data = ref.child(pk).get()
        print(
            "------------------------------------------------------------------",
            doctor_data.val(),
        )
        return render(
            request, "doctor/edit-doctor.html", {"doctor_data": doctor_data.val()}
        )
    # if not patient_data:
    #     # Handle the case where the patient with the specified ID doesn't exist
    #     # You might want to redirect to a 404 page or handle it differently based on your needs
    #     return render(request, "patient_not_found.html")

    # if request.method == "POST":
    #     # Handle the POST request to update the patient's data
    #     # Assuming you have a form with fields like first_name, last_name, email, etc.
    #     # Retrieve the updated data from the form
    #     updated_data = {
    #         "first_name": request.POST.get("first_name", ""),
    #         "last_name": request.POST.get("last_name", ""),
    #         "email": request.POST.get("email", ""),
    #         "mobile_no": request.POST.get("mobile_no", ""),
    #         "gender": request.POST.get("gender", ""),
    #         "date_of_birth": request.POST.get("date_of_birth", ""),
    #         "languages": request.POST.get("languages", ""),
    #         "nationality": request.POST.get("nationality", ""),
    #         "city": request.POST.get("city", ""),
    #         "zip_code": request.POST.get("zip", ""),
    #         "user_role": request.POST.get("user_role", ""),
    #         "address": request.POST.get("address", ""),
    #         "bio": request.POST.get("bio", ""),
    #     }

    #     # Update the patient's data in the Firebase Realtime Database
    #     ref.child(pk).update(updated_data)

    #     # Optionally, you can redirect to a different page after the update
    #     return redirect(
    #         "patient_list"
    #     )  # Replace 'patient_list' with your actual URL name

    # Handle the GET request to display the patient's data in the form

    return JsonResponse({"redirect_url": reverse("doctor_list")})


# return render(request, "edit_doctor.html", {"doctor_data": doctor_data})

@admin_only
def doctor_update(request, pk):
    if request.method == "POST":
        data_patient_update = {
            "first_name": request.POST.get("first_name", ""),
            "last_name": request.POST.get("last_name", ""),
            "email": request.POST.get("email", ""),
            "mobile_no": request.POST.get("mobile_no", ""),
            "gender": request.POST.get("gender", ""),
            "date_of_birth": request.POST.get("date_of_birth", ""),
            "languages": request.POST.get("languages", ""),
            "nationality": request.POST.get("nationality", ""),
            "city": request.POST.get("city", ""),
            "zip_code": request.POST.get("zip", ""),
            "user_role": request.POST.get("user_role", ""),
            "address": request.POST.get("address", ""),
            "bio": request.POST.get("bio", ""),
        }
        database.child("Doctors").child(pk).update(data_patient_update)

    return redirect("doctor_detail", pk=pk)

@admin_only
def doctor_delete(request, pk):
    database.child("Doctors").child(pk).remove()
    if request.headers.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest":
        # If it's an AJAX request, respond with a JSON indicating the redirect URL
        return JsonResponse({"redirect_url": reverse("doctor_list")})
    else:
        # If it's a regular form submission, perform the redirect
        return redirect("doctor_list")
    return JsonResponse({"redirect_url": reverse("doctor_list")})

    return redirect("doctor_list")


######################### Patience ######################


def patient_list(request):
    # patients = Patient.objects.all()
    # return render(request, "patient_list.html", {"patients": patients})

    Patients = database.child("Patients").get()

    return render(request, "patient/all-patients.html", {"patients": Patients.val()})


def patient_detail(request, pk):
    # patient = get_object_or_404(Patient, pk=pk)
    # return render(request, "patient/patient_detail.html", {"patient": patient})
    patient = {}
    return render(request, "patient/patient_detail.html", {"patient": patient})


def patient_create(request):
    # if request.method == "POST":
    #     form = PatientForm(request.POST)
    #     if form.is_valid():
    #         patient = form.save()
    #         return redirect("patient_detail", pk=patient.pk)
    # else:
    #     form = PatientForm()
    # return render(request, "patient_form.html", {"form": form})

    # -------------------metode Add-------------------
    print("patient_create ==================================>>>>>>>")

    data_Patients = []
    if request.method == "POST":
        # print("request", request.POST)
        data_Patients = {
            # "Prenom": request.POST["FirstName"],
            # "Nom": request.POST["LastName"],
            # "Check_in": request.POST["DateOfBirth"],
            # "Check_out": request.POST["Gender"],
            # "N_chamber": request.POST["Blood"],
            # "Prix": request.POST["CIN"],
            # "Prix_R": request.POST["CNSSNumber"],
            # "Nationalite": request.POST["Email"],
            # "Domicile": request.POST["Mobile_No"],
            "FirstName": request.POST.get("FirstName", ""),
            "LastName": request.POST.get("LastName", ""),
            "Email": request.POST.get("Email", ""),
            "Mobile_No": request.POST.get("Mobile_No", ""),
            "Birthday": request.POST.get("Birthday", ""),
            "Marital_Status": request.POST.get("Marital_Status", ""),
            "Gender": request.POST.get("Gender", ""),
            "Blood_Group": request.POST.get("Blood_Group", ""),
            "CIN": request.POST.get("Cin", ""),
            "CNSSNumber": request.POST.get("CNSSNumber", ""),
            "mutualType": request.POST.get("mutualType", ""),
            # "age": request.POST.get("age", ""),
            "typeAge": request.POST.get("typeAge", ""),
            # "Address": request.POST.get("Address", ""),mutualType
            # "Patient_History": request.POST.get("Patient_History", ""),
        }
        # Generate a unique identifier manually (rendem id)
        rendem_id = "Patient_" + str(uuid.uuid4())

        # Update the data_Patients dictionary with the rendem id
        data_Patients["Patient_id"] = rendem_id

        print(
            "Data with Unique Identifier (rendem id) before push:",
            data_Patients["typeAge"],
        )

        # Now you can push the data to Firebase using the unique identifier
        database.child("Patients").child(rendem_id).set(data_Patients)

    return render(request, "patient/new-patient.html")


def patient_edit(request, pk):
    # patient = get_object_or_404(Patient, pk=pk)
    # if request.method == "POST":
    #     form = PatientForm(request.POST, instance=patient)
    #     if form.is_valid():
    #         patient = form.save()
    #         return redirect("patient_detail", pk=patient.pk)
    # else:
    #     form = PatientForm(instance=patient)
    # return render(request, "patient_form.html", {"form": form})

    # -------------------metode Update-------------------
    if request.method == "POST":
        data_Patients = {
            "Prenom": request.POST["FirstName"],
            "Nom": request.POST["LastName"],
            "Check_in": request.POST["DateOfBirth"],
            "Check_out": request.POST["Gender"],
            "N_chamber": request.POST["Blood"],
            "Prix": request.POST["CIN"],
            "Prix_R": request.POST["CNSSNumber"],
            "Nationalite": request.POST["Email"],
            "Domicile": request.POST["Tel"],
        }
        result = (
            database.child("Patients").order_by_child("CIN").equal_to("K823753").get()
        )

        for entry in result.each():
            database.child("Patients").child(entry.val().get("Patient_id")).update(
                data_Patients
            )

    return render(request, "patient_form.html")


def patient_update(request, pk):
    if request.method == "POST":
        data_patient_update = {
            "FirstName": request.POST["first_name"],
            "LastName": request.POST["last_name"],
            "Email": request.POST["email"],
            "Mobile_No": request.POST["mobile_no"],
            "Birthday": request.POST["birthday"],
            "Marital_Status": request.POST["marital_status"],
            "Gender": request.POST["gender"],
            "Blood_Group": request.POST["blood_group"],
            "CIN": request.POST["patient_cin"],
            "CNSSNumber": request.POST["patient_cnss"],
            "mutualType": request.POST["mutualType"],
            "typeAge": request.POST.get("typeAge", ""),
            # "Address": request.POST["address"],
            # "Patient_History": request.POST["patient_history"],
            "Patient_id": request.POST["id"],
        }
        database.child("Patients").child(pk).update(data_patient_update)
    print("UPDATE =>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n")
    return JsonResponse({"status": "success"})
    # return redirect("patient_list")

@admin_only
def patient_delete(request, pk):
    # patient = get_object_or_404(Patient, pk=pk)
    # patient.delete()
    # -------------------metode delete-------------------
    database.child("Patients").child(pk).remove()
    # return redirect("patient_list")
    return JsonResponse({"status": "success"})


##################################### appointment ##################################


def appointment_list(request):
    # appointments = Appointment.objects.all()
    # return render(request, 'appointment_list.html', {'appointments': appointments})
    new_data = []
    total_lidkal = 0
    total_likhrej = 0
    total = 0
    start_date = datetime.today().strftime('01/01/%Y')
    end_date = datetime.today().strftime('%d/%m/%Y')

    data = database.child('Client').order_by_child("Fait").start_at(start_date).end_at(end_date).get()

    for entry in data.each():
        if datetime.strptime(entry.val().get('Fait'), '%d/%m/%Y') >= datetime.strptime(start_date, '%d/%m/%Y') and datetime.strptime(entry.val().get('Fait'), '%d/%m/%Y') <= datetime.strptime(end_date, '%d/%m/%Y'):
            input_date = datetime.strptime(entry.val().get('Fait'), '%d/%m/%Y')
            
            prix_str = entry.val().get('Prix')
            # Remove non-numeric characters (except for dots) from the Prix string
            prix_str = ''.join(char if char.isdigit() or char == '-' else '' for char in prix_str)

            # print(prix_str)
            if prix_str and prix_str.strip() != '':
                prix_value = int(prix_str)
                if prix_value > 0:
                    total_lidkal += prix_value
                    if int(entry.val().get("Prix_R")) == 0:
                        status = True
                    else:
                        status = False
                    new_data.append({
                        "nom" : entry.val().get("Nom"),
                        "prenom" : entry.val().get("Prenom"),
                        "Prix" : prix_value,
                        "Prix_R" : int(entry.val().get("Prix_R")),
                        "N_chamber": entry.val().get('N_chamber'),
                        "Check_in": convert_date_to_timestamp(entry.val().get('Check_in')),
                        "Check_out": convert_date_to_timestamp(entry.val().get('Check_out')),
                        "id" : entry.val().get('ID'),
                        "Fait" : input_date.strftime('%Y-%m-%d'),
                        "Status" : status,
                    })
                    # print(convert_date_to_timestamp(entry.val().get('Check_in')))
                if prix_value < 0:
                    total_likhrej += prix_value
                total += prix_value


    # print(total_lidkal)
    # print(total_likhrej)
    # print(total)
    return render(
        request,
        "appointement/new-appointment.html",
        {
            "appointments": new_data,
            "Total" : total_lidkal
        },
    )


def appointment_detail(request, pk):
    # appointment = get_object_or_404(Appointment, pk=pk)
    # return render(request, 'appointment_detail.html', {'appointment': appointment})
    return render(request, "appointment_detail.html")


def appointment_create(request):
    # if request.method == 'POST':
    #     form = AppointmentForm(request.POST)
    #     if form.is_valid():
    #         appointment = form.save()
    #         return redirect('appointment_detail', pk=appointment.pk)
    # else:
    #     form = AppointmentForm()
    # return render(request, 'appointment_form.html', {'form': form})
    return render(request, "appointement/new-appointment.html")


def appointment_edit(request, pk):
    # appointment = get_object_or_404(Appointment, pk=pk)
    # if request.method == 'POST':
    #     form = AppointmentForm(request.POST, instance=appointment)
    #     if form.is_valid():
    #         appointment = form.save()
    #         return redirect('appointment_detail', pk=appointment.pk)
    # else:
    #     form = AppointmentForm(instance=appointment)
    # return render(request, 'appointment_form.html', {'form': form})
    if request.method == "POST":
        # print(request.POST)
        data=request.POST
        # data = json.loads(request.body)
        # # print(data)
        updateData = {
            "start": data["start"],
            "end": data["end"],
            "Patient_id": data["nom"],
            "Doctor_id": data["Doctor_id"],
            # "title": data["title"] ,
            "totalPrice":data["totalPrice"],
            "typeAppointment":data['typeAppointment_update'],
            "remainingAmount":float(data["remainingAmount_update"]),
            "amountPaid":float(data["amountPaid_update"]),
            "Motif": data["motif"],
        }
        # First_Name = request.POST['nom']
        # Last_Name = request.POST['prenom']
        # Check_in = request.POST['check_in']
        # Check_out = request.POST['check_out']
        # Room = request.POST['n_chamber']
        # Prix = request.POST['prix']
        print(updateData['Motif'])
        database.child("Appointments").child(pk).update(updateData)
    return JsonResponse({"success": True})

    return render(request, "appointment_form.html")


def appointment_delete(request, pk):
    # appointment = get_object_or_404(Appointment, pk=pk)
    # appointment.delete()
    database.child("Appointments").child(pk).remove()
    if request.method == "POST":
        return JsonResponse({"success": True})
           

    return redirect("appointment_list")


################################# prescription ################################


def prescription_list(request):
    # prescriptions = Prescription.objects.all()
    # return render(request, 'prescription_list.html', {'prescriptions': prescriptions})
    return render(request, "prescriptions/all-prescriptions.html")


def prescription_detail(request, pk):
    # prescription = get_object_or_404(Prescription, pk=pk)
    # return render(request, 'prescription_detail.html', {'prescription': prescription})
    return render(request, "prescription_detail.html")


def prescription_create(request):
    # if request.method == 'POST':
    #     form = PrescriptionForm(request.POST)
    #     if form.is_valid():
    #         prescription = form.save()
    #         return redirect('prescription_detail', pk=prescription.pk)
    # else:
    #     form = PrescriptionForm()
    # return render(request, 'prescription_form.html', {'form': form})
    return render(request, "prescriptions/new-prescription.html")


def prescription_edit(request, pk):
    # prescription = get_object_or_404(Prescription, pk=pk)
    # if request.method == 'POST':
    #     form = PrescriptionForm(request.POST, instance=prescription)
    #     if form.is_valid():
    #         prescription = form.save()
    #         return redirect('prescription_detail', pk=prescription.pk)
    # else:
    #     form = PrescriptionForm(instance=prescription)
    # return render(request, 'prescription_form.html', {'form': form})
    return render(request, "prescription_form.html")


def prescription_delete(request, pk):
    # prescription = get_object_or_404(Prescription, pk=pk)
    # prescription.delete()
    return redirect("prescription_list")


#################################### drugs ############################################


def drug_create(request):
    return render(request, "drug/add-drug.html")


################################### test ###############################################


def test_list(request):
    # tests = Test.objects.all()
    # return render(request, "test_list.html", {"tests": tests})
    return render(request, "tests/all-tests.html")


def test_detail(request, pk):
    # test = get_object_or_404(Test, pk=pk)
    # return render(request, "test_detail.html", {"test": test})
    return render(request, "test_detail.html")


def test_create(request):
    # if request.method == "POST":
    #     form = TestForm(request.POST)
    #     if form.is_valid():
    #         test = form.save()
    #         return redirect("test_detail", pk=test.pk)
    # else:
    #     form = TestForm()
    # # return render(request, "test_form.html", {"form": form})
    return render(request, "tests/add-test.html")


def test_edit(request, pk):
    # test = get_object_or_404(Test, pk=pk)
    # if request.method == "POST":
    #     form = TestForm(request.POST, instance=test)
    #     if form.is_valid():
    #         test = form.save()
    #         return redirect("test_detail", pk=test.pk)
    # else:
    #     form = TestForm(instance=test)
    # return render(request, "test_form.html", {"form": form})
    return render(request, "test_form.html")


def test_delete(request, pk):
    # test = get_object_or_404(Test, pk=pk)
    # test.delete()
    return redirect("test_list")


##################################### calendar ###############################


def save_calendar(request):

    

    if request.method == "POST":
        data = json.loads(request.body)
        id = database.child('Client').order_by_child("Fait").limit_to_last(1)
        print(id)
        # print(data)
        # Save the event data to the database
        # Example: You might have a model named Event and save data like this
        test = {
            "ID": id,
            "start": data["start"],
            "end": data["end"],
            "Patient_id": data["extendedProps"]["patient_id"],
            "Doctor_id": data["extendedProps"]["doctor_id"],
            "title": data["title"],
            "Motif": data["motif"],
            # ---------------------- new data ----------------------
            "totalPrice": data["extendedProps"]["totalPrice"],
            "amountPaid": data["extendedProps"]["amountPaid"],
            # "Rest": data[""],
            "Statut_de_paiement": data["extendedProps"]["Statut_de_paiement"],
            "typeAppointment": data["extendedProps"]["typeAppointment"],
        }
        print(test)
        database.child("Appointments").child(rendem_id).set(test)

        # event.save()

        return JsonResponse({"success": True, "message": "Event saved successfully"})

    return JsonResponse({"success": False, "message": "Invalid request method"})


def calendar_edit(request, pk):
    # appointment = get_object_or_404(Appointment, pk=pk)
    # if request.method == 'POST':
    #     form = AppointmentForm(request.POST, instance=appointment)
    #     if form.is_valid():
    #         appointment = form.save()
    #         return redirect('appointment_detail', pk=appointment.pk)
    # else:
    #     form = AppointmentForm(instance=appointment)
    # return render(request, 'appointment_form.html', {'form': form})
    if request.method == "POST":
        data = json.loads(request.body)
        # print(data)
        updateData = {
            "start": data["start"],
            "end": data["end"],
            "Patient_id": data["extendedProps"]["patient_id"],
            "Doctor_id": data["extendedProps"]["doctor_id"],
            "title": data["title"],
            # "Motif": data["Motif"],
        }
        print(updateData)
        database.child("Appointments").child(pk).update(updateData)
    return JsonResponse({"success": True})

def calendar(request):
    # rendem_id = "Appointment_" + str(uuid.uuid4())

    Patients = database.child("Patients").get().val()
    Doctors = database.child("Doctors").get().val()
    # appointments = database.child("Appointments").get()

    # test = {
    #     'Appointment_id' : rendem_id,
    #     'start' : 'Thu Dec 07 2023 19:00:00 GMT+0100 (UTC+01:00)',
    #     'end' : 'Thu Dec 07 2023 19:30:00 GMT+0100 (UTC+01:00)',
    #     'Patient_id' : 'Patient_20de515d-f803-49cb-a55f-79442580b1c6',
    #     'Doctor_id' : 'Doctor_ca8f7ad2-c915-4f1a-89fb-bacbd8065120',
    #     'title' : 'cds',
    #     'Motif' : 'test Motif',
    # }

    # database.child("Appointments").child(rendem_id).set(test)

    # appointment = {
    #     "Patients": Patients.val(),
    #     "Doctors": Doctors.val(),
    #     "appointments": appointments.val(),
    # }
    # print(appointment)
    return render(
        request, "calendar/calendar.html", {"Patients": Patients, "Doctors": Doctors}
    )


##################################### Report ################################


def report_list(request):
    # reports = Report.objects.all()
    # return render(request, 'report_list.html', {'reports': reports})
    return render(request, "reports/reports.html")


def report_detail(request, pk):
    # report = get_object_or_404(Report, pk=pk)
    # return render(request, 'report_list.html', {'reports': reports})
    return render(request, "report_detail.html")


def report_create(request):
    # if request.method == 'POST':
    #     form = ReportForm(request.POST)
    #     if form.is_valid():
    #         report = form.save()
    #         return redirect('report_detail', pk=report.pk)
    # else:
    #     form = ReportForm()
    # return render(request, 'report_list.html', {'reports': reports})
    return render(request, "report_form.html")


def report_edit(request, pk):
    # report = get_object_or_404(Report, pk=pk)
    # if request.method == 'POST':
    #     form = ReportForm(request.POST, instance=report)
    #     if form.is_valid():
    #         report = form.save()
    #         return redirect('report_detail', pk=report.pk)
    # else:
    #     form = ReportForm(instance=report)
    # return render(request, 'report_form.html', {'form': form})
    return render(request, "report_form.html")


def report_delete(request, pk):
    # report = get_object_or_404(Report, pk=pk)
    # report.delete()
    return redirect("report_list")


############################ billing ##############################


def invoice_create(request):
    return render(request, "invoice/create-invoice.html")


def billing_list(request):
    return render(request, "billing/billing-list.html")


############################ settings #############################


def doctor_settings(request):
    return render(request, "doctor/doctor-settings.html")


def prescriptions_settings(request):
    data_Patients = {
        "FirstName": "test",
        "LastName": "testa",
        "Blood": "A+",
        "CNSSNumber": "77394",
        "Email": "test@test.com",
        "CIN": "K823883",
        "DateOfBirth": "20/10/2001",
        "Gender": "M",
        "Tel": "063552728",
        "Address": "hhdye jdood ejdr N4",
    }

    # -------------------metode Add-------------------
    # # Generate a unique identifier manually (rendem id)
    # rendem_id = "Patient_" + str(uuid.uuid4())

    # # Update the data_Patients dictionary with the rendem id
    # data_Patients["Patient_id"] = rendem_id

    # print("Data with Unique Identifier (rendem id) before push:", data_Patients)

    # # Now you can push the data to Firebase using the unique identifier
    # database.child("Patients").child(rendem_id).set(data_Patients)

    # -------------------metode Update-------------------
    # result = database.child("Patients").order_by_child("CIN").equal_to("K823753").get()

    # for entry in result.each():
    #     database.child("Patients").child(entry.val().get("Patient_id")).update(data_Patients)

    # -------------------metode delete-------------------
    # result = database.child("Patients").order_by_child("CIN").equal_to("K823753").get()

    # for entry in result.each():
    #     database.child("Patients").child(entry.val().get("Patient_id")).remove()

    return render(request, "test.html")















def convert_to_human_date(date_str):
    if not date_str:
        return "N/A", "N/A"

    try:
        # Try to parse as ISO 8601 date
        dt = datetime.fromisoformat(date_str)
        formatted_date = dt.strftime('%Y-%m-%d')
        formatted_time = dt.strftime('%H:%M')
        return formatted_date, formatted_time
    except ValueError:
        # If parsing as ISO 8601 fails, assume it's a timestamp in milliseconds
        try:
            timestamp_in_seconds = float(date_str) / 1000.0
            dt = datetime.fromtimestamp(timestamp_in_seconds)
            formatted_date = dt.strftime('%Y-%m-%d')
            formatted_time = dt.strftime('%H:%M')
            return formatted_date, formatted_time
        except (ValueError, TypeError):
            # Handle the case where the date_str is not a valid ISO 8601 date or timestamp
            # You might want to log a warning or handle it based on your application's requirements
            return "Invalid Date", "Invalid Time"