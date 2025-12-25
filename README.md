# RemoteVNCBooking

* Reservation tool that centralizes lab/server-room test machines in one UI.\
* It supports hourly booking/cancellation, and—when policy conditions are met—enables one-click connection to the target machine via RealVNC Viewer.

## Key Features

- **Login**: Users enter `Display Name` and `WWID` to access the main window (optional **Remember** to persist the last login).
- **Machine list grouping**: Automatically groups machines by the prefix of `sn`.
- **Hourly booking/cancellation**: Uses 0–23 as time slots (with AM/PM toggle for display) and prevents duplicate bookings.
- **Visual status indicators**
  - Time-slot buttons: available / booked / selected (color-coded)
  - Machine buttons: a top-right LED shows whether the current hour is booked
- **One-click connect**: When allowed, generates a temporary `.vnc` connection file (Host/Username/Password) and opens it via the system default handler to launch RealVNC Viewer and connect to the machine.

![Login](https://github.com/Blacktea945/RemoteVNCBooking/blob/master/pic/pic_1.png)
![Main](https://github.com/Blacktea945/RemoteVNCBooking/blob/master/pic/pic_2.png)
![Booking](https://github.com/Blacktea945/RemoteVNCBooking/blob/master/pic/pic_3.png)
