

frappe.ui.form.on('Leave Application' , {
    refresh: function(frm){
        ResetReferance(frm);
    }, 
    onload: function(frm){
        ResetReferance(frm);
    }, 
    setup: function(frm){
        ResetReferance(frm);
    }, 
});


function ResetReferance(frm){
    if (frm.doc.docstatus === 0 ){
        frm.doc.custom_sla_reference = null; 
        refresh_field("custom_sla_reference");
        }
}
