<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Attendance Deduction Request</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
        }
        .container {
            max-width: 600px;
            margin: 20px auto;
            padding: 20px;
            background-color: #fff;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        h1, p {
            margin: 0;
        }
        .message {
            margin-top: 20px;
        }
        .footer {
            margin-top: 20px;
            font-size: 12px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Attendance Deduction Request</h1>
        <p>Dear Attendance Department,</p>
        <div class="message">
            <p>This is to inform you that an employee's attendance needs to be deducted due to the following reason:</p>
            <p><strong>Employee Name:</strong> {{doc.employee}}</p>
            <p><strong>Reason:</strong> {{doc.employee_reason}}</p>
            <p>Please proceed with the necessary deduction in the attendance records.</p>
        </div>
        <div class="footer">
            <p>Best Regards,<br> {{frappe.session.user}}<br></p>
        </div>
    </div>
</body>
</html>
