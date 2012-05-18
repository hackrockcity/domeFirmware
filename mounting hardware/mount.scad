board_width = 45;
board_thickness = 1.85;
board_separation = 27;

platform_thickness = 2;

module ledge() {
  union() {
    cube(size = [6.5,platform_thickness,board_width]);
    translate([0,platform_thickness+board_thickness,0])
      cube(size = [6.5,platform_thickness,board_width]);

//    translate([0,platform_thickness+1,0])
//      rotate(a=[90,0,0])
//        translate([6,3,0])
//          cylinder(h=platform_thickness+1,r=1.3);

//    translate([0,platform_thickness+1,board_width-6])
//      rotate(a=[90,0,0])
//        translate([6,3,0])
//          cylinder(h=platform_thickness+1,r=1.3);
  }
}

module mount() {
  translate([-8,0,0]) {

    difference() {
      cube(size=[8,platform_thickness,board_width]);

      translate([0,platform_thickness+.25,0])
        rotate(a=[90,0,0])
          translate([4,5,0])
            cylinder(h=platform_thickness+.5,r=1.7);

      translate([0,platform_thickness+.25,board_width-6])
        rotate(a=[90,0,0])
          translate([4,1,0])
            cylinder(h=platform_thickness+.5,r=1.7);
    }
  }
}

difference() {
  cube(size = [4,2*board_separation+platform_thickness*2+board_thickness,board_width]);
  translate([-.5,6,5])
    cube(size=[5,20,board_width-10]);
  translate([-.5,6+board_separation,5])
    cube(size=[5,20,board_width-10]);
}

mount();


translate([4,0,0])
  ledge();
translate([4,board_separation,0])
  ledge();
translate([4,board_separation*2,0])
  ledge();