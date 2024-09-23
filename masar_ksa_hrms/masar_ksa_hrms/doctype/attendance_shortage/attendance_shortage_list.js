frappe.listview_settings['Attendance Shortage'] = {
    onload: function(list) {
        list.page.add_inner_button(
            __('Get Employees'),
            function() {
                let dialog = frappe.prompt(
                    [
                        {
                            fieldname: 'department',
                            fieldtype: 'Link',
                            label: __('Department'),
                            options: 'Department',
                            bold: 1
                        },
                        {
                            fieldname: 'nationality',
                            fieldtype: 'Link',
                            label: __('Nationality'),
                            options: 'Country',
                            bold: 1
                        },
                        {
                            fieldname: 'default_shift',
                            fieldtype: 'Link',
                            label: __('Default Shift'),
                            options: 'Shift Type',
                            bold: 1
                        },
                        {
                            fieldname: 'posting_date',
                            fieldtype: 'Date',
                            label: __('Posting Date'),
                            'default': frappe.datetime.get_today(),
                            reqd: 1,
                            bold: 1,
                            onchange: function() {
                                frappe.call({
                                    method: "masar_ksa_hrms.masar_ksa_hrms.doctype.attendance_shortage.attendance_shortage.get_date_period_list",
                                    args: {
                                        posting_date: this.value
                                    },
                                    callback: function(response) {
                                        if (response.message) {
                                            let from_date = response.message.from_date;
                                            let to_date = response.message.to_date;

                                            dialog.set_value('date_from', from_date);
                                            dialog.set_value('date_to', to_date);
                                        }
                                    }
                                });
                            }
                        },
                        {
                            fieldname: 'date_from',
                            fieldtype: 'Date',
                            label: __('From Date'),
                            reqd: 1,
                            bold: 1,
                            read_only: 1
                        },
                        {
                            fieldname: 'date_to',
                            fieldtype: 'Date',
                            label: __('To Date'),
                            reqd: 1,
                            bold: 1,
                            read_only: 1
                        },
                    ],
                    function(values) {
                        frappe.call({
                            method: "masar_ksa_hrms.masar_ksa_hrms.doctype.attendance_shortage.attendance_shortage.get_employees",
                            args: {
                                department: values.department,
                                nationality: values.nationality,
                                default_shift: values.default_shift,
                                posting_date: values.posting_date ,
                                date_from: values.date_from,
                                date_to: values.date_to
                            },
                        });
                    },
                    __('Employees Data'),
                    __('Get Employees')
                );
            },
            null,
            'primary'
        );
    }
};