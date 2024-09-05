#!/bin/bash

if [ ! -d "./mods" ]
then
   mkdir ./mods
fi
mv -f *.chi ./mods
mv -f *.f01 ./mods
mv -f *.qva ./mods
mv -f *.atm ./mods


if [ ! -d "./modelli" ]
then
   mkdir ./modelli
fi
mv -f 0* ./modelli
mv -f 1* ./modelli

if [ ! -d "./out" ]
then
   mkdir ./out
fi

if [ -a "grafi" ]
then
   cd out 
   if [ -a "a01-gra" ]
   then
      for nomefile in a*-gra ; do
         numero=10#${nomefile:1:2}
      done
      let "numero += 1"
      if [ $numero -lt 10 ] ; then
         aaa="a0"${numero}
      else
         aaa="a"${numero}
      fi
   else
      aaa="a01"
   fi
   cd ..
   nomina $aaa
   mv -f $aaa* ./out
   echo "aggiunto pacco n. $aaa"
fi

cd out
if [ -a "a01-gra" ]
then
   cp a01-gra grafica
   echo "copiato a01-gra in grafica"
   for nomefile in a*-gra ; do
      if [ $nomefile != "a01-gra" ] ; then
         echo "aggiunto $nomefile a grafica"
         u_uniscigra grafica $nomefile
      fi
   done
else
   exit 'pippa matricolata, a01-gra non esiste!'
fi

if [ -s "a01-datirot" ]
then
   cp a01-datirot datirot
   echo "copiato a01-datirot in datirot"
   for nomefile in a*-datirot ; do
      if [ $nomefile != "a01-datirot" ] ; then
         echo "aggiunto $nomefile a datirot"
         uniscirot datirot $nomefile
      fi
   done
else
   echo 'a01-datirot non esiste!'
fi


if [ -a "a01-mlo" ]
then
   cp a01-mlo wind.ful
   echo "copiato a01-mlo in wind.ful"
   for nomefile in a*-mlo ; do
      if [ $nomefile != "a01-mlo" ] ; then
         echo "aggiunto $nomefile a wind.ful"
         unisciwind wind.ful $nomefile
      fi
   done
   wind wind.ful wind.rid
else
   echo 'non ci sta perdita di massa'
fi

if [ -a "network" ]
then
  u_incolall grafica wind.rid grafica
else
   cp ../network .
   u_incolall grafica wind.rid grafica
fi

if [ ! -d "../grafica" ]
then
   mkdir ../grafica
fi
mv -f ccwind ../grafica
mv -f gra_chimica_cen ../grafica
mv -f gra_chimica_sup ../grafica
mv -f gra_fisica ../grafica
mv -f lista_abbondanti ../grafica
mv -f shellHHeconv ../grafica
mv -f varieta ../grafica
if [ -s "datirot" ]
then
   cp -f datirot ../grafica
fi

if [ ! -d "../analisi" ]
then
   mkdir ../analisi
fi
cd ../analisi
#idl -e "basica2b"
exit
