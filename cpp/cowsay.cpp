#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <cmath>
#include <cstdio>

const std::size_t k_max_length = 60;

std::string format(const std::vector<std::string> &content, std::size_t max_length)
{
    std::cout << "max_length: " << content.size() << std::endl;
    std::string formatted;
    std::string v_sep_l = "|";
    std::string v_sep_r = "|";
    formatted.append(std::string(" ") + std::string(max_length + 2, '-') + std::string(" "));
    for (const auto &line : content)
    {
        formatted.append("\n");
        formatted.append(v_sep_l);
        formatted.append(" ");
        formatted.append(line + std::string(max_length - line.length(), ' '));
        formatted.append(" ");
        formatted.append(v_sep_r);
    }
    formatted.append("\n");
    formatted.append(std::string(" ") + std::string(max_length + 2, '-') + std::string(" "));
    return formatted;
}

std::string convert_tab_to_space(const std::string &src)
{
    auto line = src;
    const auto search = "\t";
    for (int i = line.find(search); i >= 0; i = line.find(search))
    {
        line.replace(i, 1, "    ");
    }
    return line;
}

std::uint32_t get_line_max_length(const std::string &line, std::size_t max_length)
{
    return std::min(k_max_length, std::max(max_length, line.length()));
}

void append_normalized(std::vector<std::string> &content, const std::string &str, std::size_t length)
{
    if (str.length() <= length)
    {
        content.emplace_back(str);
    }
    else
    {
        for (std::size_t i = 0; i < str.length(); i += length)
        {
            content.emplace_back(str.substr(i, length));
        }
    }
}

std::vector<int> rgb(int i)
{
    double f = 0.1;
    return {int(std::sin(f * double(i) + 0.0) * 127 + 128),
            int(std::sin(f * double(i) + 2.0 * M_PI / 3.0) * 127 + 128),
            int(std::sin(f * double(i) + 4.0 * M_PI / 3.0) * 127 + 128)};
}

std::istream &safe_getline(std::istream &is, std::string &t)
{
    t.clear();

    // The characters in the stream are read one-by-one using a std::streambuf.
    // That is faster than reading them one-by-one using the std::istream.
    // Code that uses streambuf this way must be guarded by a sentry object.
    // The sentry object performs various tasks,
    // such as thread synchronization and updating the stream state.

    std::istream::sentry se(is, true);
    std::streambuf *sb = is.rdbuf();

    for (;;)
    {
        int c = sb->sbumpc();
        switch (c)
        {
        case '\n':
            return is;
        case '\r':
            if (sb->sgetc() == '\n')
                sb->sbumpc();
            return is;
        case std::streambuf::traits_type::eof():
            // Also handle the case when the last line has no line ending
            if (t.empty())
                is.setstate(std::ios::eofbit);
            return is;
        default:
            t += (char)c;
        }
    }
}

int main()
{
    std::size_t max_length = 0;
    std::vector<std::string> content;
    while (std::cin.peek() != std::char_traits<char>::eof())
    {
        std::string line;
        safe_getline(std::cin, line);
        line = convert_tab_to_space(line);
        append_normalized(content, line, max_length = get_line_max_length(line, max_length));
    }

    std::string formmatted = format(content, max_length);

    const char cow[] = R"(         \  ^__^
          \ (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||
)";

    const char yoda[] = R"(               \
                \
                    _.' :  `._               
                .-.'`.  ;   .'`.-.           
        __     / : ___\ ;  /___ ; \      __  
      ,'_ ""--.:__;".-.";: :".-.":__;.--"" _`,
      :' `.t""--.. '<@.`;_  ',@>` ..--""j.' `;
          `:-.._J '-.-'L__ `-- ' L_..-;'     
            "-.__ ;  .-"  "-.  : __.-"       
                L ' /.------.\ ' J           
                 "-.   "--"   .-"
)";

    formmatted.append("\n");
    formmatted.append(yoda);

    // std::cout << formmatted << std::endl;

    auto i = 0;
    for (const auto &c : formmatted)
    {
        auto color = rgb(i++);
        char output[50] = {};
        std::snprintf(output, 50, "\033[38;2;%d;%d;%dm%c\033[0m", color[0], color[1], color[2], c);
        std::cout << output;
    }
    return 0;
}
