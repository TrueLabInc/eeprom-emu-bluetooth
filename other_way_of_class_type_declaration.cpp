#include <iostream>
using std::cout;
using std::endl;

class Baza
{
public:
	char* string;
	Baza(char* string) : string(string) {};
	void pisz()
   {
      std::cout << string << std::endl;
   }
	int ret(){
		return 10;
	}
};

class Baza2 : public Baza
{
public:
   void pisz()
   {
      std::cout << "Tu funkcja pisz z klasy Baza2" << std::endl;
   }
};

int main(){
	   Baza k = Baza("rafal");
	   k.pisz();
}
