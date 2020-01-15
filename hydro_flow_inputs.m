%Import data as table, dates and times don't convert to array - drop them
%and convert to double
mobileriver30 = MobileRiverupdate(:,3);
mobileriver30 = table2array(mobileriver30);
mobileriver15 = mobileriver30(83425:372384); %10/4/2010 is when 15min increments begin
mobileriver30 = mobileriver30(1:83424);

n = 48; % average every n values
b = arrayfun(@(i) nanmean(mobileriver30(i:i+n-1)),1:n:length(mobileriver30)-n+1)'; % the averaged vector

n2 = 96;
b2 = arrayfun(@(i) nanmean(mobileriver15(i:i+n-1)),1:n:length(mobileriver15)-n+1)'; 
b3 = cat(1,b,b2);

b3 = 0.0283168*b3; %converting to metric flow
h = Mobilestage(:,3);
h = table2array(h);
h = 0.3048*h; %converting to meters
blah = arrayfun(@(i) nanmean(h(i:i+n-1)),1:n:length(h)-n+1)'; % the averaged vector
h_h = -104.8*((blah).^2)+(1039*blah)+22.83;
Q = 0.000184*(b3.^2) + 0.6388*blah +32.7;

x = isnan(tensaw);
tensaw(x) = Q(x);
x = 1:length(b3) ;
b4(isnan(b4)) = interp1(x(~isnan(b3)),b3(~isnan(b3)),x(isnan(b3))) ;

%tarbertlanding
tarbert = MRTarbertLanding(:,2);
tarbert = table2array(tarbert);

%tensaw
tensaw = TensawRiverupdate(:,3);
tensaw = table2array(tensaw);
tensaw = tensaw(39505:410566);
tensaw15 = tensaw(84747:371062);
tensaw30 = tensaw(1:84746);
n=48;
b = arrayfun(@(i) nanmean(tensaw30(i:i+n-1)),1:n:length(tensaw30)-n+1)';

n = 96; % average every n values
b2 = arrayfun(@(i) nanmean(tensaw15(i:i+n2-1)),1:n2:length(tensaw15)-n2+1)'; % the averaged vector
b3 = cat(1,b,b2);

x = 1:length(b3) ;
tensaw2 = b3;
tensaw2(isnan(tensaw2)) = interp1(x(~isnan(b3)),b3(~isnan(b3)),x(isnan(b3))) ;
[row, col] = find(isnan(tensaw2));

tensaw2 = 0.0283168*tensaw2;

%biloxi
bil = BiloxiRiverupdate(:,2);
bil = table2array(bil);
bil = bil*0.0283168;
[row, col] = find(isnan(bil));
x = 1:length(bil) ;
bil2 = bil;
bil2(isnan(bil2)) = interp1(x(~isnan(bil)),bil(~isnan(bil)),x(isnan(bil))) ;

%natalbany
nat = NatalbanyRiverupdate(:,2);
nat = table2array(nat);
nat = nat*0.0283168;
[row, col] = find(isnan(nat));
x = 1:length(nat) ;
nat2 = nat;
nat2(isnan(nat2)) = interp1(x(~isnan(nat)),nat(~isnan(nat)),x(isnan(nat))) ;

%pasagoula
pasa = PascagoulaRiverdaily(:,2);
pasa = table2array(pasa);
pasa = pasa*0.0283168;

[row, col] = find(isnan(pasa));

%Lafourche
laf = GIWWLafourcheQ1(:,3);
laf = table2array(laf);
laf = laf*0.0283168;
[row, col] = find(isnan(laf));
n3 = 4;
laf2 = arrayfun(@(i) nanmean(laf(i:i+n3-1)),1:n3:length(laf)-n3+1)';

giww = GIWWHoumaQ(:,3);
giww = table2array(giww);
giww = giww*0.0283168;
giww2 = arrayfun(@(i) nanmean(giww(i:i+n3-1)),1:n3:length(giww)-n3+1)';

giwwh = GIWWHoumH1(:,3);
giwwh = table2array(giwwh);
giwwh = giwwh*0.3048;
giwwh2 = arrayfun(@(i) nanmean(giwwh(i:i+n3-1)),1:n3:length(giwwh)-n3+1)';
Q = 0.0009914*(giww2.^2) + 0.4895*giwwh2 + 9.37;
x = isnan(laf2);
laf2(x) = Q(x);
[row, col] = find(isnan(laf2));
x = 1:length(laf2);
laf3 = laf2;
laf3(isnan(laf3)) = interp1(x(~isnan(laf2)),laf2(~isnan(laf2)),x(isnan(laf2))) ;

x = 1:length(giww2);
giww3 = giww2;
giww3(isnan(giww3)) = interp1(x(~isnan(giww2)),giww2(~isnan(giww2)),x(isnan(giww2))) ;

%different lafourche
la = BayouLafourcheupdate(:,2);
la = table2array(la);
la = la*0.0283168;
lah = BayouLafourchestage(:,4);
lah = table2array(lah);
lah = lah*0.3048;
Q = 3.62*lah.^2+ -2.359*lah + 2.392;
la2 = la;
x = isnan(la);
la2(x) = Q(x);
[row, col] = find(isnan(lafourche2));

x = 1:length(la2) ;
la3 = la2;
la3(isnan(la3)) = interp1(x(~isnan(la2)),la2(~isnan(la2)),x(isnan(la2))) ;

%GIWW Larose and Houma
GIWW = GIWWLaroseupdate(:,3);
GIWW = table2array(GIWW);
GIWW = GIWW*0.0283168;
n3 = 4;
GIWW2 = arrayfun(@(i) nanmean(GIWW(i:i+n3-1)),1:n3:length(GIWW)-n3+1)'; %consolidating to hourly
[row, col] = find(isnan(GIWW2)); %how much data is missing

GIWWHouma = GIWWHoumaupdate(:,3);
GIWWHouma = table2array(GIWWHouma);
GIWWHouma = GIWWHouma*0.0283168;
GIWWHouma2 = arrayfun(@(i) nanmean(GIWWHouma(i:i+n3-1)),1:n3:length(GIWWHouma)-n3+1)'; %consolidating to hourly

stage = HoumadailyH(:,2);
stage = table2array(stage);
stage = stage*0.3048;
GIWWHouma3 = GIWWHouma2(1:3559);
Q = 0.0009914*(GIWWHouma3.^2) + 0.4895*stage +9.37;

GIWW3 = GIWW2(1:3559);
x = isnan(GIWW3);
GIWW4 = GIWW3;
GIWW4(x) = Q(x);

x = 1:length(GIWW2) ;
GIWW3(isnan(GIWW3)) = interp1(x(~isnan(GIWW2)),GIWW2(~isnan(GIWW2)),x(isnan(GIWW2))) ;

%Neches
Neches = NechesBeaumontTX15update(:,3);
Neches = table2array(Neches);
Neches = Neches*0.0283168;
Neches = arrayfun(@(i) nanmean(Neches(i:i+n2-1)),1:n2:length(Neches)-n2+1)';
[row, col] = find(isnan(Neches));

NechesE = NechesRiverTXupdate(:,4);
NechesE = table2array(NechesE);
NechesE = NechesE*0.0283168;

Q = 1.533*NechesE +-13.83;
x = isnan(Neches);
Neches2 = Neches;
Neches2(x) = Q(x);

%mermentau
mermq = MermQ15ch(:,3);
mermq = table2array(mermq);
mermq = mermq*0.0283168;
mermq = arrayfun(@(i) nanmean(mermq(i:i+n3-1)),1:n3:length(mermq)-n3+1)';
[row, col] = find(isnan(mermq));

mermh = MermH15ch(:,3);
mermh = table2array(mermh);
mermh = mermh*0.3048;

mermh = arrayfun(@(i) nanmean(mermh(i:i+n3-1)),1:n3:length(mermh)-n3+1)'; %consolidating to hourly
Q = 71.16*((mermh).^2) + 179.2*mermh + -110;
x = isnan(mermq);
mermq2 = mermq;
mermq2(x) = Q(x);
x = 1:length(mermq2) ;
mermq3 = mermq2;
mermq3(isnan(mermq3)) = interp1(x(~isnan(mermq2)),mermq2(~isnan(mermq2)),x(isnan(mermq2))) ;
[row, col] = find(isnan(mermq3));


%bayou lacassine
Qla = 0.00007014*(mermq.^2)+0.2057*mermh+2.266;
%equation is wrong in the appendix
x = 1:length(Qla) ;
Qla2 = Qla;
Qla2(isnan(Qla2)) = interp1(x(~isnan(Qla)),Qla(~isnan(Qla)),x(isnan(Qla))) ;
[row, col] = find(isnan(Qla2));

%Vermilion Surrey
verm = VermSQ(:,3);
verm = table2array(verm);
verm = verm*0.0283168;
n3 = 4;
verm2 = arrayfun(@(i) nanmean(verm(i:i+n3-1)),1:n3:length(verm)-n3+1)'; %consolidating to hourly
[row, col] = find(isnan(verm2)); %how much data is missing
x = 1:length(verm2) ;
verm3 = verm2;
verm3(isnan(verm3)) = interp1(x(~isnan(verm2)),verm2(~isnan(verm2)),x(isnan(verm2))) ;
%Vermilion Perry
vermp = VermPQ(:,3);
vermp = table2array(vermp);
vermp = vermp*0.0283168;
vermp2 = arrayfun(@(i) nanmean(vermp(i:i+n3-1)),1:n3:length(vermp)-n3+1)'; %consolidating to hourly
[row, col] = find(isnan(vermp2)); %how much data is missing
Q = 0.9284*verm2+10.26;
x = isnan(vermp2);
vermp3 = vermp2;
vermp3(x) = Q(x);
x = 1:length(vermp3) ;
vermp4 = vermp3;
vermp4(isnan(vermp4)) = interp1(x(~isnan(vermp3)),vermp3(~isnan(vermp3)),x(isnan(vermp3))) ;

%GIWW Franklin and Wax Lake
frank = GIWWSale(:,3);
frank = table2array(frank);
frank = frank*0.0283168;
frank2 = arrayfun(@(i) nanmean(frank(i:i+n3-1)),1:n3:length(frank)-n3+1)';

wax = WaxLake(:,3);
wax = table2array(wax);
wax = wax*0.0283168;
wax2 = arrayfun(@(i) nanmean(wax(i:i+n3-1)),1:n3:length(wax)-n3+1)';
x = 1:length(wax2) ;
wax3 = wax2;
wax3(isnan(wax3)) = interp1(x(~isnan(wax2)),wax2(~isnan(wax2)),x(isnan(wax2))) ;

Q = .08815*wax + -13.34;
x = isnan(frank2);
frank3 = frank2;
frank3(x) = Q(x);
[row, col] = find(isnan(frank3));
x = 1:length(frank3) ;
frank4 = frank3;
frank4(isnan(frank4)) = interp1(x(~isnan(frank3)),frank3(~isnan(frank3)),x(isnan(frank3))) ;

%Teche
teche = Teche(:,3);
teche = table2array(teche);
teche = teche*0.0283168;
teche2 = arrayfun(@(i) nanmean(teche(i:i+n3-1)),1:n3:length(teche)-n3+1)';

char = Charentondaily(:,2);
char = table2array(char);
char = char*0.0283168;

stage = CharentonH(:,2);
stage = table2array(stage);
stage = stage*0.3048;

Qc = -0.1165*(teche.^2) + 13.57*stage + -75.82;

[row, col] = find(isnan(char));
x = isnan(char);
char2 = char;
char2(x) = Qc(x);
[row, col] = find(isnan(char2));

x = 1:length(char3) ;
char4 = char3;
char4(isnan(char4)) = interp1(x(~isnan(char3)),char3(~isnan(char3)),x(isnan(char3))) ;

x = 1:length(teche) ;
teche2 = teche;
teche2(isnan(teche2)) = interp1(x(~isnan(teche)),teche(~isnan(teche)),x(isnan(teche))) ;