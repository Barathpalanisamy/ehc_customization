<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Forwarding Late Entry for Salary Review</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
        }
        .container {
            max-width: 600px;
            margin: 20px auto;
            padding: 20px;
            background-color: #f4f4f4;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        .header {
            background-color: #007bff;
            color: #fff;
            padding: 10px;
            border-radius: 8px 8px 0 0;
        }
        .content {
            padding: 20px;
        }
        .footer {
            background-color: #f0f0f0;
            padding: 10px;
            border-radius: 0 0 8px 8px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>Forwarding Late Entry for Salary Review</h2>
        </div>
        <div class="content">
            <p>Dear HR Team,</p>
            <p>Please review the late entry of {{doc.employee}} for salary consideration.</p>
            Reason: {{doc.employee_reason}}</p>
            <p>Thank you for your attention to this matter.</p>
            <p>Sincerely,<br>{{doc.user}}</p>
        </div>
    </div>
</body>
</html>
