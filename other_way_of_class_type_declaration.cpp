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


int main(){
	   Baza k = Baza("rafal");
	   k.pisz();
}
