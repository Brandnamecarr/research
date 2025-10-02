#include <iostream>
#include <fstream>
#include <mutex>
#include <unordered_map>
#include <string>
#include <sstream>

// dummy service that a singleton will be made from
class ConfigManager {

    public:
    static ConfigManager* getInstance(std::string configFile="data.txt")
    {
        if (instance == nullptr)
        {
            instance = new ConfigManager(configFile);
        }
        return instance;
    }
    private:
    static ConfigManager* instance;
    std::unordered_map<std::string, std::string> configData;
    bool parsedFile;
    
    ConfigManager(std::string &configFile)
    {
        loadConfig(configFile);
    }

    // Helper to load config
    void loadConfig(const std::string& filename) {
        std::ifstream file(filename);
        if (!file) {
            std::cerr << "Error: Could not open config file.\n";
            return;
        }

        std::string line;
        while (std::getline(file, line)) {
            std::istringstream iss(line);
            std::string key, value;
            if (std::getline(std::getline(iss, key, '='), value)) {
                configData[key] = value;
            }
        }
        std::cout << "Config loaded successfully.\n";
        parsedFile = true; // once the config has been loaded, set this to true // 
    } // loadConfig () //

    public:

    void printConfig()
    {
        for (const auto & kv: configData)
        {
            std::cout << kv.first << " = " << kv.second << std::endl;
        }
    } // printConfig() //

    std::string get(const std::string &key)
    {
        if (configData.count(key))
        {
            return configData[key];
        }
        return {};
    }

    bool parsed()
    {
        // if there is data and we have parsed the file //
        if (!configData.empty() && parsedFile)
        {
            return true;
        }
        return false;
    } // parsed() //

}; // ConfigManager // 


ConfigManager *ConfigManager::instance = nullptr;

int main(int argc, char** argv)
{
    std::cout << "Hello, world from app" << std::endl;

    ConfigManager* cfg = ConfigManager::getInstance("data.txt");
    std::cout << "host = " << cfg->get("host") << std::endl;
    std::cout << "port = " << cfg->get("port") << std::endl;

    cfg->printConfig();
    return 0;
}