  //Parametri
  base_raggio = 100;
  base_altezza = 50;
  base_spessoreb = 10;
  base_b = base_raggio - base_spessoreb;
  colonna_altezza = 150;
  colonna_n = 3;
  colonna_raggio = 10;
  tetto_raggio = base_raggio + (base_raggio*20/100);    
  tetto_altezza = 80;  
  sfera_raggio = tetto_raggio - (tetto_raggio*30/100);

module mangiatoia()
{
  //Disegno della base
  translate([0, 0, -120]) {
    difference() {
      cylinder(h = base_altezza, r = base_raggio);
      translate([0, 0, colonna_raggio]) cylinder(h = base_altezza, r = base_b);
      //translate([base_raggio, 0, 35]) cube(50, center = true);
    }
    // Disegno delle colonne
    for (i = [0:(colonna_n-1)]) {
      echo(360*i/colonna_n, sin(360*i/colonna_n)*base_b, cos(360*i/colonna_n)*base_b);
      translate([sin(360*i/colonna_n)*base_b, cos(360*i/colonna_n)*base_b, 0 ])
        cylinder(h = colonna_altezza, r=colonna_raggio);
    }
    // Disegno del tetto
    difference() {
    translate([0, 0, colonna_altezza])
      cylinder(h = tetto_altezza, r1 = tetto_raggio, r2 = 0);
    translate([0, 0, colonna_altezza - sfera_raggio/2])
      sphere(sfera_raggio);
    }
  }
}

echo(version=version());

rotate(a=[0,180,0]) mangiatoia();
