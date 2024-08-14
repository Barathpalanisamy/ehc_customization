<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Late Reason Approved</title>
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
        <h1>Late Reason Approved</h1>
        <p>Dear {{doc.employee}},</p>
        <div class="message">
            <p>Your reason for being late has been approved by your manager. Please note the following details:</p>
            <p><strong>Reason:</strong> {{doc.employee_reason}}</p>
            <p>You are permitted to arrive late on the specified date due to the reason provided. Ensure to make up for the lost time accordingly.</p>
        </div>
        <div class="footer">
            <p>Best Regards,<br> {{frappe.session.user}}<br></p>
        </div>
    </div>
</body>
</html>
