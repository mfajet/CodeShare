#############################################################################
# Generated by PAGE version 4.8.9
# in conjunction with Tcl version 8.6
set vTcl(timestamp) ""


set vTcl(actual_gui_bg) #d9d9d9
set vTcl(actual_gui_fg) #000000
set vTcl(actual_gui_menu_bg) #d9d9d9
set vTcl(actual_gui_menu_fg) #000000
set vTcl(complement_color) #d9d9d9
set vTcl(analog_color_p) #d9d9d9
set vTcl(analog_color_m) #d9d9d9
set vTcl(active_fg) #000000
set vTcl(actual_gui_menu_active_bg)  #d8d8d8
set vTcl(active_menu_fg) #000000
#################################
#LIBRARY PROCEDURES
#


if {[info exists vTcl(sourcing)]} {

proc vTcl:project:info {} {
    set base .top37
    namespace eval ::widgets::$base {
        set dflt,origin 0
        set runvisible 1
    }
    set site_3_0 $base.scr45
    namespace eval ::widgets_bindings {
        set tagslist _TopLevel
    }
    namespace eval ::vTcl::modules::main {
        set procs {
        }
        set compounds {
        }
        set projectType single
    }
}
}

#################################
# USER DEFINED PROCEDURES
#

#################################
# GENERATED GUI PROCEDURES
#

proc vTclWindow.top37 {base} {
    if {$base == ""} {
        set base .top37
    }
    if {[winfo exists $base]} {
        wm deiconify $base; return
    }
    set top $base
    ###################
    # CREATING WIDGETS
    ###################
    vTcl::widgets::core::toplevel::createCmd $top -class Toplevel \
        -background {#d9d9d9} 
    wm focusmodel $top passive
    wm geometry $top 772x539+509+259
    update
    # set in toplevel.wgt.
    global vTcl
    set vTcl(save,dflt,origin) 0
    wm maxsize $top 1351 738
    wm minsize $top 1 1
    wm overrideredirect $top 0
    wm resizable $top 1 1
    wm deiconify $top
    wm title $top "CodeSharer"
    vTcl:DefineAlias "$top" "Toplevel1" vTcl:Toplevel:WidgetProc "" 1
    label $top.lab39 \
        -background {#d9d9d9} -foreground {#000000} -text {Output here} 
    vTcl:DefineAlias "$top.lab39" "Label1" vTcl:WidgetProc "Toplevel1" 1
    button $top.but40 \
        -activebackground {#d9d9d9} -background {#d9d9d9} \
        -command {lambda : print("HI")} -foreground {#000000} \
        -highlightcolor black -text Run 
    vTcl:DefineAlias "$top.but40" "Button1" vTcl:WidgetProc "Toplevel1" 1
    label $top.lab41 \
        -anchor w -background {#d9d9d9} -foreground {#000000} -justify left \
        -text {Who's typing:} 
    vTcl:DefineAlias "$top.lab41" "Label2" vTcl:WidgetProc "Toplevel1" 1
    vTcl::widgets::ttk::scrolledtext::CreateCmd $top.scr45 \
        -background {#d9d9d9} -height 468 -highlightcolor black -width 398 
    vTcl:DefineAlias "$top.scr45" "Scrolledtext1" vTcl:WidgetProc "Toplevel1" 1

    $top.scr45.01 configure -background white \
        -font TkTextFont \
        -foreground black \
        -height 3 \
        -highlightcolor black \
        -insertbackground black \
        -insertborderwidth 3 \
        -selectbackground #c4c4c4 \
        -selectforeground black \
        -takefocus 0 \
        -undo 1 \
        -width 10 \
        -wrap none
    ###################
    # SETTING GEOMETRY
    ###################
    place $top.lab39 \
        -in $top -x 400 -y 40 -width 366 -relwidth 0 -height 468 -relheight 0 \
        -anchor nw -bordermode ignore 
    place $top.but40 \
        -in $top -x 371 -y 10 -width 50 -height 26 -anchor nw \
        -bordermode ignore 
    place $top.lab41 \
        -in $top -x 0 -y 510 -width 766 -relwidth 0 -height 28 -relheight 0 \
        -anchor nw -bordermode ignore 
    place $top.scr45 \
        -in $top -x 0 -y 40 -width 398 -relwidth 0 -height 468 -relheight 0 \
        -anchor nw -bordermode ignore 

    vTcl:FireEvent $base <<Ready>>
}

#############################################################################
## Binding tag:  _TopLevel

bind "_TopLevel" <<Create>> {
    if {![info exists _topcount]} {set _topcount 0}; incr _topcount
}
bind "_TopLevel" <<DeleteWindow>> {
    if {[set ::%W::_modal]} {
                vTcl:Toplevel:WidgetProc %W endmodal
            } else {
                destroy %W; if {$_topcount == 0} {exit}
            }
}
bind "_TopLevel" <Destroy> {
    if {[winfo toplevel %W] == "%W"} {incr _topcount -1}
}

Window show .
Window show .top37

